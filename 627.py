import os
import datetime
import sys
from operator import itemgetter
from flask import Flask, request, redirect, url_for, send_from_directory, render_template
from werkzeug import secure_filename

UPLOAD_FOLDER = "./uploadedfile/"
ALLOWED_EXTENSIONS = set(['txt','csv'])
app = Flask(__name__)
app.config['UPLOAD_FOLDER']=UPLOAD_FOLDER
app.config['MAX_CONTENT_LENGTH']=5*1024*1024

# Dictionary for team
dic_team = {"nalakuvara":"Nalakuvara",
			"deep_learning":"Deep Learning",
			"silver":"Silver",
			"z":"Z",
			"phinex":"Phinex",
			"explorer":"Explorer",
			"xjbz2206":"XJBZ2206"}
dic_team_file = {"nalakuvara":"1_nalakuvara.txt",
				"deep_learning":"2_deep_learning.txt",
				"silver":"3_silver.txt",
				"z":"4_z.txt",
				"phinex":"5_phinex.txt",
				"explorer":"6_explorer.txt",
				"xjbz2206":"7_xjbz2206.txt"}

# Data File				
RANK_FILE = "ranking.txt"
LOG_FILE = "upload_log.txt"
TURE_FILE = "TrueResult.txt"

# Filter out file extension
def allowed_file(filename):
	return '.' in filename and \
		filename.rsplit('.',1)[1] in ALLOWED_EXTENSIONS
		
# Homepage, upload file
@app.route("/", methods=['GET','POST'])
def upload_file():
	correct_rate =  0
	try:
		if request.method == 'POST':
			file = request.files['file']
			if file and allowed_file(file.filename):
				filename = secure_filename(file.filename)
				file.save(os.path.join(app.config['UPLOAD_FOLDER'],filename))
				return redirect(url_for('uploaded_file',filename=filename,teamName=request.form['team']))
		return	render_template("upload_file.html")
	except RequestEntityTooLarge:
		error = "File is too large!"
		return render_template("error.html",error = error)
		

# Uploaded file and return correct rate
@app.route("/<filename>")
def uploaded_file(filename):
	testData = []
	trueData = []
	teamName = request.args.get("teamName")
	upload_time = datetime.datetime.now()-datetime.timedelta(hours=5)
	#try:
	# Load uploaded test file
	with open(os.path.join(app.config['UPLOAD_FOLDER'],filename)) as testFile:
		for line in testFile:
			testData.append(line.strip("\n").strip("\r"))
	# Load True Result
	with open(TURE_FILE) as trueFile:
		for line in trueFile:
			trueData.append(line.strip("\n").strip("\r"))
	# Calculate correct rate
	if len(testData) == len(trueData):
		ans = [ 1 if i == j else 0 for i,j in zip(testData,trueData)]
		correct_rate = "%.4f"%(float(sum(ans))/float(len(ans)))
		with open("teamLog/"+dic_team_file[teamName],"a") as teamLogFile:
			with open(LOG_FILE,"a") as logFile:
				wString = upload_time.strftime("%Y-%m-%d %H:%M:%S")+"|From Team:"+teamName+"|Correct Rate: %.4f"%(float(sum(ans))/float(len(ans)))+"\n"
				logFile.write(wString)
				teamLogFile.write(wString)
				
		os.remove(os.path.join(app.config['UPLOAD_FOLDER'],filename))
		
		# Update Leader board
		rank_list = []
		with open(RANK_FILE) as rankFile:
			for item in rankFile:
				temp_list = item.strip("\n").strip("\r").split("|")
				temp_list[2] = float(temp_list[2])
				rank_list.append(temp_list)
		
		update_bool = 0
		for line in rank_list:
			if line[0]==teamName:
				if float(correct_rate)>line[2]:
					line[2] = float(correct_rate)
					line[3] = upload_time.strftime("%Y-%m-%d %H:%M:%S")
					update_bool = 1
						
		if update_bool:
			rank_list = sorted(rank_list, key=itemgetter(2), reverse=True)
			with open(RANK_FILE,"w") as rankFile:
				for line in rank_list:
					rankFile.write("|".join(line[:2])+"|"+"%.4f"%line[2]+"|"+line[3]+"\n")
		
		return	render_template("uploaded_file.html",correct_rate="Correct Rate is " + correct_rate, 
							teamName=dic_team[teamName], date=upload_time.strftime("%Y-%m-%d %H:%M:%S"))
	else:
		error = "Length doesn't match"
		return render_template("error.html",error = error)
	
	#except FileNotFoundError:
	#	error = "File does not exist"
	#	return render_template("error.html",error = error)
	
# Leader Board
@app.route("/ranking")
def cur_ranking():
	rank_list = []
	i=1
	with open("ranking.txt") as rankFile:
		for item in rankFile:
			temp=item.strip("\n").strip("\r").split("|")
			temp[0]=dic_team[temp[0]]
			rank_list.append([i]+temp)
			i=i+1
	return render_template("leader_board.html",rankList = rank_list)
	
if __name__=="__main__":
	app.debug = True
	app.run(host='0.0.0.0')
