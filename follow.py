import database
from tools import login_required, valid_args, errorDB
from flask import Flask, flash, session, redirect, request, render_template, url_for

@login_required
def session_followers():
	result = "Error: get"
	args = (str(session.get('id', None)),)
	if not valid_args(args):
		return 'Error: argument'
	result = database.DB.select("SELECT user_followed_id FROM public.user_follow WHERE user_follow_id = %s;", args, "all")
	if result == -1:
		return -1
	followed = []
	if result:
		for row in result:
			followed.append(int(row[0]))

	session['user_follow'] = followed
	return 0

@login_required
def follow():
	result = "Error: get"
	if request.method == 'GET':
		args = (session['id'], int(request.args.get('user_id', None)))
		if not valid_args(args):
			return 'invalid arguments', 400
			#return redirect(url_for('search'))
		if args[1] in session['user_follow']:
			return "Error: already followed", 400
		result = database.DB.insert("INSERT INTO public.user_follow (user_follow_id, user_followed_id) VALUES (%s, %s);", args)
		if result == -1:
			return errorDB, 500
		if result != 1:
			return "user not found", 404

		if session_followers() == -1:
			return errorDB, 500
		session['post_likes'].append(int(args[1]))
		session['follow'] += 1
		args = (args[1],)
		result = database.DB.select("SELECT public.user.* FROM public.user WHERE public.user.id = %s;", args)
		if result == -1:
			return errorDB, 500
		return render_template("single_user_follow.html", user = result), 200

		#return redirect(url_for('back_to_search')), status_code
	return str(result), 405

def do_unfollow(user_id):
	args = (session['id'], user_id)
	if not valid_args(args):
		return -1
	if args[1] not in session['user_follow']:
		return -2
	result = database.DB.insert("DELETE FROM public.user_follow WHERE user_follow_id = %s AND user_followed_id = %s;", args)
	if result == -1:
		return -1
	#session['post_likes'].append(int(args[1]))
	session['follow'] -= 1
	return (result)

@login_required
def unfollow():
	result = "Error: get"
	if request.method == 'GET':
		#user = ()

		args = (session['id'], int(request.args.get('user_id', None)))
		if not valid_args(args):
			return "invalid arguments", 400
			#return redirect(url_for('search'))

		if args[1] not in session['user_follow']:
			return "user not followed", 404
			#return redirect(url_for('search'))
		result = database.DB.insert("DELETE FROM public.user_follow WHERE user_follow_id = %s AND user_followed_id = %s;", args)
		if result == -1:
			return errorDB, 500
		if result != 1:
			return "user not found", 404
		if session_followers() == -1:
			return errorDB, 500
		session['post_likes'].append(int(args[1]))
		session['follow'] -= 1
		return "user unfollowed", 200
	return str(result), 405

@login_required
def unfollow_blog():
	status_code = 200
	res = do_unfollow(int(request.args.get('user_id', None)))
	if res == -1:
		return errorDB, 500
	if res != 1:
		status_code = 404
		return "user not found", 404
	return "user unfollowed", 200

@login_required
def follows_unfollow():
	result = "Error: get"
	status_code = 200
	if request.method == 'GET':
		args = (session['id'], int(request.args.get('user_id', None)))
		if not valid_args(args):
			return redirect(url_for('my_follows'))

		if args[1] not in session['user_follow']:
			return redirect(url_for('my_follows'))
		result = database.DB.insert("DELETE FROM public.user_follow WHERE user_follow_id = %s AND user_followed_id = %s;", args)
		if result == -1:
			return errorDB, 500
		if result != 1:
			status_code = 404
		else:
			session['post_likes'].append(int(args[1]))
			session['follow'] -= 1
		return redirect(url_for('my_follows')), status_code
	return str(result), 405

@login_required
def my_follows():
	status_code = 200
	args = (str(session['id']))
	result = database.DB.select("SELECT public.user.* FROM public.user_follow LEFT JOIN public.user ON (public.user_follow.user_followed_id = public.user.id) WHERE public.user_follow.user_follow_id = %s;", args, "all")
	if result == -1:
		return errorDB, 500
	if result != 1:
		status_code = 404
	return render_template('my_follows.html', users = result), status_code

@login_required
def my_followers():
	status_code = 200
	args = (str(session['id']))
	result = database.DB.select("SELECT public.user.* FROM public.user_follow LEFT JOIN public.user ON (public.user_follow.user_follow_id = public.user.id) WHERE public.user_follow.user_followed_id = %s;", args, "all")
	if result == -1:
		return errorDB, 500
	return render_template('my_followers.html', users = result), status_code