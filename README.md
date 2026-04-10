# KanMind Backend API

This project was built as part of my backend training at the Developer Akademie.

The goal was to create a clean and structured REST API for a Kanban-style task management app using Django and Django REST Framework.  
I focused on keeping the code readable, modular and as close as possible to a real-world setup (especially permissions and data handling).

---

##  What this project does

- User registration & login (token-based authentication)
- Create and manage boards
- Add members to boards
- Create, update and delete tasks
- Assign users (assignee / reviewer)
- Comment system for tasks
- Basic but realistic permission logic

---

##  Tech Stack

- Python
- Django
- Django REST Framework
- Token Authentication

---

##  Getting started

Clone the repository:

git clone <your-repo-url>  
cd kanmind-backend  

Create a virtual environment:

python -m venv venv  
venv\Scripts\activate   # Windows  

Install dependencies:

pip install -r requirements.txt  

Run migrations:

python manage.py migrate  

Start the server:

python manage.py runserver  

API runs on:  
http://127.0.0.1:8000/

---

##  Authentication

Token-based authentication is used.

Register:
POST /api/registration/

Login:
POST /api/login/

Example response:

{
  "token": "...",
  "fullname": "...",
  "email": "...",
  "user_id": 1
}

Use the token:

Authorization: Token YOUR_TOKEN

---

##  Main endpoints

### Boards

GET /api/boards/ → all boards (owner/member)  
POST /api/boards/ → create board  
GET /api/boards/{id}/ → board details  
PATCH /api/boards/{id}/ → update board  
DELETE /api/boards/{id}/ → delete (owner only)  

---

### Tasks

POST /api/tasks/ → create task  
PATCH /api/tasks/{id}/ → update task  
DELETE /api/tasks/{id}/ → delete task  

GET /api/tasks/assigned-to-me/ → assigned tasks  
GET /api/tasks/reviewing/ → reviewing tasks  

---

### Comments

GET /api/tasks/{task_id}/comments/ → list comments  
POST /api/tasks/{task_id}/comments/ → create comment  
DELETE /api/tasks/{task_id}/comments/{comment_id}/ → delete comment  

---

### Email check

GET /api/email-check/?email=test@mail.com  

---

##  Permissions

I tried to keep permissions simple but realistic:

- Authentication required for most endpoints
- Board:
  - Owner → full access
  - Members → read & update
- Tasks:
  - Only board members can interact
  - Delete → creator or board owner
- Comments:
  - Only author can delete

---

##  Project structure

core/  
auth_app/  
kanban_app/  
    api/  

---

##  Notes

- Built during my Developer Akademie backend training
- Focus on clean structure and understandable logic
- No database or virtual environment included
- API follows the given endpoint documentation

---

##  Status

Backend is functional and ready to be used with a frontend.
