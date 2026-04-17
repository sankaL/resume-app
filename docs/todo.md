# TODO

Codex
- [x] Rename app to Applix
- [x] create new logo
- [x] Allow applications to be deleted from the applications table
- [x] Add multi-select for delete and multi-mark-as-applied in applications table
- [x] Make the text, the job title text, and the badge on status columns horizontally aligned in the applications table. 
- [x] Add a delete button in the applications table in the action column and add a delete button on the application details page Next to the export PDF button.
- [x] Add a way to delete There are sometimes there are extractions that are cute that are stuck in that state forever so I need a way to stop the extraction so that it can be deleted force stop the extraction. 
- [x] too many lines on the dashbaord move things around?
- [] saving profile changes - fails with 500 also make the e-mail
- [x] Align filters on applications table with the search bar
- [] Only create draft/application if URL is provided; don't create if closed with no input
- [x] The next fix I’d make is to hard-block generation/regeneration when the stored job data looks like blocked-source placeholder text, and route the app back to manual-entry recovery instead.
- [x] Update login page to reflect current UI state

Opus
- [x] Add breadcrumb ("Home") to dashboard page it looks empty "Home"
- [x] Replace "Applied" checkbox with a button at end of table to toggle applied status
- [x] Add confirmation modal when marking application as applied
- [x] Make resume markdown editing mode look prettier (add styling)
- [x] Make base resume editor markdown form look prettier
- [x] Add toast notifications for: application creation, deletion, etc
- [x] On bigger screens the ui is only taking up a small section of the page, make all the pages responsive in smaller and bigger screens
- [x] Various UI improvements in application detail page


- [x] In the extraction some some sections are not being grabbed just a job to description. I want to grab the entire description in the job description. Example Accenture. Not just grab the job description part. I wante tod grab the qualifications everything about the j job also even grab the salary if it's provided I think that should be a new field as part of the application. We need to do a schema change. 
- [x] add the things that will change in the configuration when the user is selecting low, medium, high so that they know exactly what is what will be affected If it's too much information to put, make the configuration card smaller with a tooltip that shows all the details. 
- [x] In the aggressiveness high, I wanted to even change the professional experience titles. Not the dates of the titles, but the actual title name to change it to match whatever experience that I'm putting in. low and medium mode do not touch the titles of any of my roles 

- [x] fix the resume output pdf issues - too small now use the latest example. make the job experience bold on pdf.
- [x] Add sign up flow when only invite only. Where is the invite triggered and what is the flow to sign up for new users and make their account and then log in. Test that out before launch. z-ai/glm-5.1 or 

- [x] seems like companies are striped away from the experience section - test first before fixing to see if its one off thing - maybe change modal
- [] Create a test suite integration in pytest with reporting request library - i make the scenarios sanity test suite



- [x] The medium agressiveness doesnt seem that aggressive explore the rules and make some changes.
- [x] Suggesstion for improving ai writing from https://claude.ai/chat/628ee097-fa6f-48e3-a1e0-d0b34c2f23bc
- [] The export dropdown is cut off on desktop mode. 
See if I can use five point four mini extra high with reasoning instead of five point four to cost save or Or Gemini three flash with reasoning. 
- [] Add a diff in the markdown preview and edit mode so we can see what was injected and what was changed from the base resume. When a resume is generated, I want the UI to show um in the generated section in markdown editable mode and the non-editable mode what was added in line, not separately, but in line. Is that possible? I want added content to be in a different color. Use an external library if there exists for doing diffs on markdown to markdown or text to text. No need to write your own functionality if not required. 
    - [] Or show a toggle to do a split screen between the base resume and the generated resume so the user can see the differences. 


- [] New updates are decent but seem only the summary and the skills are being changed now. I don't see the experience bullet points and the role title being changed at all in medium or high. 

- [] Ask Claude to come up with some rules to validate the human readable aspect and the ATS score essentially. Um come up with a prompt to score it and then I want it to run this validator after each generation and display it. Uh if it's low we can regenerate with reasons. 

- [] When configs are changed after generation in the UI, it resets back to the original but I think the actual request is sent in the backend. Just on the frontend it looks like it's the same config. 


Couple of issues:
1. Turn on medium reasoning for the full generation and partial generation. Right now it's at none 
2. somehow the aggressiveness is not adjusting to the resume at all. Maybe the controls are too tight for medium and high.


fetch("http://localhost:54800/api/applications/bea5e419-2393-42a5-abee-6a98a1b75f8d", {
  "headers": {
    "accept": "*/*",
    "accept-language": "en,fr;q=0.9,fr-CA;q=0.8",
    "authorization": "Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxNjFjOGE5Yy0zYzFlLTQzZTEtOWEyOS05OTdhNWQ4ZWE2ODMiLCJhdWQiOiJhdXRoZW50aWNhdGVkIiwiZXhwIjoxNzc2MzA1Njk0LCJpYXQiOjE3NzYzMDIwOTQsImVtYWlsIjoiaW52aXRlLW9ubHlAZXhhbXBsZS5jb20iLCJwaG9uZSI6IiIsImFwcF9tZXRhZGF0YSI6eyJwcm92aWRlciI6ImVtYWlsIiwicHJvdmlkZXJzIjpbImVtYWlsIl19LCJ1c2VyX21ldGFkYXRhIjp7ImVtYWlsX3ZlcmlmaWVkIjp0cnVlfSwicm9sZSI6ImF1dGhlbnRpY2F0ZWQiLCJhYWwiOiJhYWwxIiwiYW1yIjpbeyJtZXRob2QiOiJwYXNzd29yZCIsInRpbWVzdGFtcCI6MTc3NjAzMjE0N31dLCJzZXNzaW9uX2lkIjoiM2RhOGJjZmUtNzRhNC00MmFiLWFhOWUtMjZkYWM1MjAzYTVkIiwiaXNfYW5vbnltb3VzIjpmYWxzZX0.f_l5MTLUtIbSgoH_R1EF2FDTq4cKtxT5olGSzcevNp8",
    "content-type": "application/json",
    "sec-ch-ua": "\"Chromium\";v=\"146\", \"Not-A.Brand\";v=\"24\", \"Google Chrome\";v=\"146\"",
    "sec-ch-ua-mobile": "?0",
    "sec-ch-ua-platform": "\"macOS\"",
    "sec-fetch-dest": "empty",
    "sec-fetch-mode": "cors",
    "sec-fetch-site": "same-site"
  },
  "referrer": "http://localhost:5173/",
  "body": null,
  "method": "GET",
  "mode": "cors",
  "credentials": "include"
});

Request URL
http://localhost:54800/api/applications/bea5e419-2393-42a5-abee-6a98a1b75f8d
Request Method
GET
Status Code
500 Internal Server Error
Remote Address
[::1]:54800
Referrer Policy
strict-origin-when-cross-origin