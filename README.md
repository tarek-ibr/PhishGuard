# PhishGuard
This chrome extention uses machine learning to detect phishing websites based on URL features like HTTPS presence, domain length, and special characters. Trained on datasets from UCI, the model classifies sites as phishing or legitimate.

### Extension Installation
1.	Open Chrome Extensions (chrome://extensions/)
2.	Enable Developer Mode
3.	Load Unpacked Extension
4.	Select project directory

### Data Flow:
1.	User navigates to URL → Background script intercepts
2.	URL sent to Flask API → Feature extraction
3.	Features processed through ML model → Prediction returned
4.	If phishing is detected → Redirect to warning page
5.	User chooses to proceed or go back safely

### Architecture
PhishGuard follows a three-tier architecture comprising the browser extension frontend, local API backend, and trained ML model.



### Dataset Information:
•	Source: UCI PhiUSIIL Phishing URL Dataset
•	Size: 235,795 samples
•	Features: 56 original features (reduced to 20 key features)
•	Classes: Binary (0 = Legitimate, 1 = Phishing)


### Note: if you have better dataset with just two columns(the url and the label) you can train it using the code starting from cell (In 149) and get better model 
