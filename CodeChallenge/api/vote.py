from flask import Blueprint, jsonify, current_app, request, abort, render_template
from flask_jwt_extended import (get_current_user, jwt_required)
from flask_limiter.util import get_remote_address
from flask_mail import Message
from itsdangerous import URLSafeSerializer
from sqlalchemy import or_, func
import numpy as np

from .. import core
from ..limiter import limiter
from ..auth import Users
from ..mail import mail
from ..mailgun import mg_validate
from ..models import Answer, db, Vote, Question, ranking

bp = Blueprint("voteapi", __name__, url_prefix="/api/v1/vote")


@bp.before_request
def time_gate():
    if not core.challenge_ended():
        r = jsonify(status="error",
                    reason="voting unavailable until code challenge ends")
        r.status_code = 403
        abort(r)


@bp.route("/check", methods=["GET"])
def vote_check():
    return jsonify(status="success",
                   reason="voting is open")


@bp.route("/ballot", methods=["GET"])
@jwt_required
def get_contestants():
    """Contestants are only qualified if they answered
    the max rank question and the initial answer is correct"""

    try:
        page = int(request.args.get("page", 1))
        per = int(request.args.get("per", 20))
        desc = request.args.get("desc")
    except ValueError:
        return jsonify(status="error",
                       reason="invalid 'page' or 'per' parameter"), 400

    user = get_current_user()
    q = Answer.query.with_entities(
        Answer.id,
        Answer.text,
        func.count(Answer.votes),
        Users.studentfirstname,
        Users.studentlastname,
        Users.username,
        func.concat(Users.studentfirstname, func.right(Users.studentlastname, 1)),
        Answer.disqualified,
    ) \
        .join(Answer.question) \
        .join(Answer.user) \
        .outerjoin(Answer.votes) \
        .filter(Question.rank == core.max_rank(), Answer.correct) \
        .group_by(Answer.id)

    if desc is not None:
        q = q.order_by(func.count(Answer.votes).desc())
    else:
        q = q.order_by(Answer.id)

    p = q.paginate(page=page, per_page=per)
    itemList = []
    for _ballot in p.items:
        ballot = list(_ballot)
        ballot.append(len(Vote.query.filter_by(answer_id=ballot[0], user_id=user.id).all()) > 0)
        itemList.append(ballot)

    return jsonify(
        items=itemList,
        totalItems=p.total,
        page=p.page,
        totalPages=p.pages,
        hasNext=p.has_next,
        nextNum=p.next_num,
        hasPrev=p.has_prev,
        prevNum=p.prev_num,
        totalVotes=len(Vote.query.filter_by(user_id=user.id).all())
    )

@bp.route("/<int:answer_id>/castvote", methods=["POST"])
@jwt_required
def vote_cast(answer_id: int):
    """Cast a vote on an Answer"""
    max_rank = core.max_rank()

    ans = Answer.query \
        .join(Answer.question) \
        .filter(Answer.id == answer_id,
                Question.rank == max_rank,
                Answer.correct) \
        .first()

    if ans.disqualified is not None:
        return jsonify(status="error",
                       reason=f"This user was disqualified: {ans.disqualified}"), 400

    if ans is None:
        return jsonify(status="error",
                       reason="Qualifying answer not found"), 400

    user = get_current_user()

    v = Vote()
    v.answer_id = ans.id
    v.user_id = user.id

    # see if you already voted for this
    if Vote.query.filter_by(answer_id=answer_id, user_id=user.id).all():
        return jsonify(status="error",
                       reason="You already voted for this answer."), 400
    if len(Vote.query.filter_by(user_id=user.id).all()) > 2:
        return jsonify(status="error",
                       reason="You can only vote for a max of 3 people!"), 400
    db.session.add(v)
    db.session.commit()


    return jsonify(status="success",
                   reason="You have voted!")

@bp.route("/<int:answer_id>/castunvote", methods=["POST"])
@jwt_required
def unvote_cast(answer_id: int):
    """Revoke a vote on an Answer"""
    max_rank = core.max_rank()

    ans = Answer.query \
        .join(Answer.question) \
        .filter(Answer.id == answer_id,
                Question.rank == max_rank,
                Answer.correct) \
        .first()

    if ans.disqualified is not None:
        return jsonify(status="error",
                       reason=f"This user was disqualified: {ans.disqualified}"), 400

    if ans is None:
        return jsonify(status="error",
                       reason="Qualifying answer not found"), 400

    user = get_current_user()

    # see if you already voted for this
    if len(Vote.query.filter_by(answer_id=answer_id, user_id=user.id).all()) == 0:
        return jsonify(status="error",
                       reason="You have not voted for this answer."), 400

    v = Vote.query.filter_by(answer_id=answer_id, user_id=user.id).first()
    db.session.delete(v)
    db.session.commit()


    return jsonify(status="success",
                   reason="You have revoked your vote!")


@bp.route("/confirm", methods=["POST"])
def vote_confirm():
    try:
        token = request.json["token"]
    except KeyError:
        return jsonify("'token' missing from JSON body"), 400

    s = URLSafeSerializer(current_app.config["SECRET_KEY"])

    valid, vote_id = s.loads_unsafe(token, "vote-confirmation")

    if not valid:
        return jsonify(status="error",
                       reason="token is not valid"), 400

    v = Vote.query.get(vote_id)
    if not v:
        return jsonify(status="error",
                       reason="vote not found - try voting again, or contestant may have been disqualified.")

    if v.confirmed:
        return jsonify(status="success",
                       reason="vote already confirmed")

    delete_votes = Vote.query \
        .filter(Vote.voter_email == v.voter_email,
                Vote.id != v.id) \
        .all()

    # delete any other vote that was clicked
    for d in delete_votes:
        db.session.delete(d)

    v.confirmed = True

    db.session.commit()

    msg = Message(subject="Vote confirmation successful!",
                  recipients=[v.voter_email])

    votes, rank = v.ranking()

    msg.html = render_template("challenge_vote_submitted.html",
                               username=v.answer.user.username,
                               votes=int(votes),
                               rank=rank)

    mail.send(msg)

    return jsonify(status="success",
                   reason="vote confirmed")


@bp.route("/search", methods=["GET"])
@jwt_required
def search():
    keyword = request.args.get("q")
    try:
        page = int(request.args.get("page", 1))
        per = int(request.args.get("per", 20))
    except ValueError:
        return jsonify(status="error",
                       reason="invalid 'page' or 'per' parameter"), 400

    if keyword is None:
        return jsonify(status="error", reason="missing 'q' parameter"), 400

    keyword = f"%{keyword}%"

    user = get_current_user()

    p = Answer.query.with_entities(
        Answer.id,
        Answer.text,
        func.count(Answer.votes),
        Users.studentfirstname,
        Users.studentlastname,
        Users.username,
        func.concat(Users.studentfirstname, func.right(Users.studentlastname, 1))
    ) \
        .join(Answer.question) \
        .join(Answer.user) \
        .outerjoin(Answer.votes) \
        .filter(Question.rank == core.max_rank(), Answer.correct,
                or_(Users.username.ilike(keyword), Users.studentfirstname.ilike(keyword),
                Users.studentlastname.ilike(keyword))) \
        .group_by(Answer.id)\
        .paginate(page=page, per_page=per)

    itemList = []
    for _ballot in p.items:
        ballot = list(_ballot)
        ballot.append(len(Vote.query.filter_by(answer_id=ballot[0], user_id=user.id).all()) > 0)
        itemList.append(ballot)
    return jsonify(
        items=itemList,
        totalItems=p.total,
        page=p.page,
        totalPages=p.pages,
        hasNext=p.has_next,
        nextNum=p.next_num,
        hasPrev=p.has_prev,
        prevNum=p.prev_num
    )
