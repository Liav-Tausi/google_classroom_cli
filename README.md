<div align="left">by liav tausi</div>
<div align="center">
    <img src="https://www.linkpicture.com/q/class-room-cli.png" width="150">
    <h2 align="center">Google Classroom CLI </h2>
</div>

**Google Classroom CLI** is a **command-line interface** tool that allows users to interact with **Google Classroom** without leaving the terminal. The tool is intended for development, **teachers, and students** to have an easier and more efficient interface. The CLI supports the **same functionalities** as the Google Classroom web interface + **the ability to fill up a provided json file tamplate for a very quick & detailed action**.

```bash

main.py [-h] [-s {courses,aliases,announcements,course_work,student_submissions,course_work_materials,students,teachers,topics,invitations,user_profiles}]
               [-m {d_create,q_create,delete,get,list,d_patch,q_patch,modify,return,accept}] [--ref_cache REF_CACHE] [--c_id C_ID] [--d_json] [--ann_text ANN_TEXT] [--ann_id ANN_ID] [--materials MATERIALS] [--state STATE] [--states STATES] [--s_time S_TIME] [--u_time U_TIME] [--assi_mode ASSI_MODE] [--s_options S_OPTIONS] [--p_size P_SIZE] [--o_by O_BY] [--p_token P_TOKEN] [--a_s_ids A_S_IDS] [--r_s_ids R_S_IDS] [--title TITLE] [--desc DESC] [--w_type W_TYPE] [--c_w_id C_W_ID] [--sub_id SUB_ID] [--due_date DUE_DATE] [--due_time DUE_TIME] [--u_id U_ID] [--sub_states SUB_STATES] [--late LATE] [--assi_grade ASSI_GRADE] [--s_answer S_ANSWER] [--alt_link ALT_LINK] [--assi_sub ASSI_SUB] [--c_w_m_id C_W_M_ID] [--c_w_m_states C_W_M_STATES] [--m_link M_LINK] [--m_drive_id M_DRIVE_ID] [--i_s_options I_S_OPTIONS] [--enr_code ENR_CODE] [--t_name T_NAME] [--top_id TOP_ID] [--inv_id INV_ID] [--name NAME] [--section SECTION] [--room ROOM] [--o_id O_ID] [--desc_h DESC_H] [--s_id S_ID] [--t_id T_ID] [--alias ALIAS] [--t_email T_EMAIL] [--inv_role INV_ROLE]

```
- Note for anything more then creating a course, you will need a google worspace account

### The CLI supports three types of users:


<details>
  <summary>Admin</summary>
  
  ```python
   "account" "role" "service" "method" "**parameters"
     (a)      (r)     (-s)     (-m)     (--params)
        
    courses
        d_create (d_json)
        q_create (name, section, descn, room, o_id, state)
        delete (c_id)
        d_patch (d_json)
        q_patch (name, section, desc, desc_h, materials)
        update (d_json)
        get (c_id)
        list (s_id, t_id, states, p_size, p_token)

     aliases
        q_create (c_id, alias)
        delete (c_id, alias)
        list (c_id, p_size, p_token)

     teachers
        q_create (c_id, t_email)
        delete (c_id, t_email)
        get (c_id, t_email)
        list (c_id, p_size, p_token)

     invitations
        accept (inv_id)
        q_create (c_id, u_id, inv_role)
        delete (inv_id)
        get (inv_id)
        list (c_id, u_id, p_size, p_token)

     user_profiles
        get (u_id)
```
 </details>
 
<details>

  <summary>Teacher</summary>
  
```python
     "account" "role" "service" "method" "**parameters"
        (a)      (r)     (-s)     (-m)      (--params)

    announcement: 
          d_create (d_json)
          q_create (c_id, ann_text, materials, state, s_time, u_time, assi_mode, s_options)
          delete (c_id, ann_id)
          get (c_id, ann_id)
          list (states, p_size, o_by, p_token)
          modify (c_id, ann_id, assi_mode, a_st_ids, r_s_ids)
          d_patch (d_json)
          q_patch (c_id, ann_id, state, text, s_time)
        
    course_work:
          d_create (d_json)
          q_create (c_id, title, desc, materials, w_type, state)
          delete (c_id, c_w_id)
          get (c_id, c_w_id)
          list (c_id, states, o_by, p_size, p_token)
          modify (c_id, c_w_id, assi_mode, a_st_ids, r_s_ids)
          d_patch (d_json)
          q_patch (c_id, c_w_id, title, desc, d_date, d_time, s_time, states, materials)

    student_submissions
          get (c_id, c_w_id, sub_id)
          list (c_id, c_w_id, u_id, p_size, sub_states, late, p_token)
          modify (c_id, c_w_id, sub_id, materials)
          d_patch (detailed_json)
          q_patch (c_id, c_w_id, sub_id, sub_states, assi_grade, s_answer, alt_link, assi_sub)
          return (c_id, c_w_id, sub_id)
         
    course_work_materials
          d_create (d_json)
          q_create (c_id, title, desc, materials)
          delete (c_id, c_w_m_id)
          get (c_id, c_w_m_id)
          list (c_id, c_w_m_states, p_size, p_token, or_by, m_link, m_d_id)
          d_patch (d_json)
          q_patch (c_id, c_w_m_id, title, desc, material, s_time, states, i_s_options)
        
    students:
          q_create (c_id, enr_code, u_id)
          d_create (d_json)
          delete (c_id, u_id)
          get (c_id, u_id)
          list (c_id, p_size, p_token)
        
     topics:
          q_create (c_id, t_name)
          delete (c_id, t_id)
          get (c_id, t_id)
          list (c_id, p_size, p_token)
          q_patch (c_id, t_id, t_name)
        
     invitations:
          accept (inv_id)
```
</details>

<details>
  <summary>Student</summary>
  
 ```python
     "account" "role" "service" "method" "**parameters"
        (a)     (r)      (-s)     (-m)     (--params)
        
    student_submissions:
        turn_in (c_id, c_w_id, sub_id)
        reclaim (c_id, c_w_id, sub_id)
        
    invitation:
        accept (inv_id)     
 ```
</details>

### Getting Started

#### To use Google Classroom CLI, follow the instructions below:

#### 1. Clone the repository:
```bash
git clone https://github.com/<username>/google_classroom_cli.git
```

#### 2. Install the required packages:
```bash
pip install -r requirements.txt
```
#### 3. Set up Google Classroom API credentials by following these [instructions](https://developers.google.com/classroom/guides/authenticate).

#### 4. Start the CLI:
```bash
python main.py
```
#### 5. Follow the CLI prompts to access and interact with your Google Classroom.
<details>
  <summary>Prompts </summary>

```bash
usage: main.py [-h] [-s {courses,aliases,announcements,course_work,student_submissions,course_work_materials,students,teachers,topics,invitations,user_profiles}]
               [-m {d_create,q_create,delete,get,list,d_patch,q_patch,modify,return,accept}] [--ref_cache REF_CACHE] [--c_id C_ID] [--d_json] [--ann_text ANN_TEXT] [--ann_id ANN_ID] [--materials MATERIALS] [--state STATE] [--states STATES] [--s_time S_TIME] [--u_time U_TIME] [--assi_mode ASSI_MODE] [--s_options S_OPTIONS] [--p_size P_SIZE] [--o_by O_BY] [--p_token P_TOKEN] [--a_s_ids A_S_IDS] [--r_s_ids R_S_IDS] [--title TITLE] [--desc DESC] [--w_type W_TYPE] [--c_w_id C_W_ID] [--sub_id SUB_ID] [--due_date DUE_DATE] [--due_time DUE_TIME] [--u_id U_ID] [--sub_states SUB_STATES] [--late LATE] [--assi_grade ASSI_GRADE] [--s_answer S_ANSWER] [--alt_link ALT_LINK] [--assi_sub ASSI_SUB] [--c_w_m_id C_W_M_ID] [--c_w_m_states C_W_M_STATES] [--m_link M_LINK] [--m_drive_id M_DRIVE_ID] [--i_s_options I_S_OPTIONS] [--enr_code ENR_CODE] [--t_name T_NAME] [--top_id TOP_ID] [--inv_id INV_ID] [--name NAME] [--section SECTION] [--room ROOM] [--o_id O_ID] [--desc_h DESC_H] [--s_id S_ID] [--t_id T_ID] [--alias ALIAS] [--t_email T_EMAIL] [--inv_role INV_ROLE]
               a r

Google Classroom CLI is a command-line interface tool
that allows users to interact with Google Classroom without leaving the terminal.
This project is currently under construction and is still a work in progress.
Created by: Liav Tausi

positional arguments:
  a                     personal email or workspace account
  r                     role, admin / student / teacher

optional arguments:
  -h, --help            show this help message and exit
  -s {courses,aliases,announcements,course_work,student_submissions,course_work_materials,students,teachers,topics,invitations,user_profiles}
                        the service to use choose from: [courses, aliases, announcements, course_work, student_submissions, course_work_materials, students, teachers, topics, invitations, user_profiles]
  -m {d_create,q_create,delete,get,list,d_patch,q_patch,modify,return,accept}
                        the method to use choose from: [d_create', q_create, delete, get, list, d_patch, q_patch, modify, return, accept]
  --ref_cache REF_CACHE  refresh cache month in months, default 12 months
  --c_id C_ID           the ID of the course
  --d_json              is detailed JSON full
  --ann_text ANN_TEXT   the text of the announcement
  --ann_id ANN_ID       the ID of the announcement
  --materials MATERIALS the materials to post
  --state STATE         the state of the service
  --states STATES       the states of the service
  --s_time S_TIME       the scheduled time
  --u_time U_TIME       the update time
  --assi_mode ASSI_MODE the assignee mode
  --s_options S_OPTIONS
                        the options for students
  --p_size P_SIZE       the page size
  --p_size P_SIZE the page size
--o_by O_BY           the order by
  --p_token P_TOKEN     the page token
  --a_s_ids A_S_IDS     the student IDs to add
  --r_s_ids R_S_IDS     the student IDs to remove
  --title TITLE         the title of the service
  --desc DESC           the description of the service
  --w_type W_TYPE       the type of the course work
  --c_w_id C_W_ID       the ID of the course work
  --sub_id SUB_ID       the ID of the student submission
  --due_date DUE_DATE   the due date of the service
  --due_time DUE_TIME   the due time of the service
  --u_id U_ID           the user ID
  --sub_states SUB_STATES
                        the sub states of the service
  --late LATE           whether the submission is late
  --assi_grade ASSI_GRADE
                        the assigned grade
  --s_answer S_ANSWER   the short answer
  --alt_link ALT_LINK   the alternate link
  --assi_sub ASSI_SUB   the submission for the assignment
  --c_w_m_id C_W_M_ID   the ID of the course work material
  --c_w_m_states C_W_M_STATES
                        status of this course work material
  --m_link M_LINK       the link to the material
  --m_drive_id M_DRIVE_ID
                        the Google Drive ID of the material
  --i_s_options I_S_OPTIONS
                        the options for individual students
  --enr_code ENR_CODE   the enrollment code for the course
  --t_name T_NAME       the name of the topic
  --top_id TOP_ID       the ID of the topic
  --inv_id INV_ID       the ID of the invitation
  --name NAME           name of the course
  --section SECTION     section of the course
  --room ROOM           room of the course
  --o_id O_ID           Id of the owner of course
  --desc_h DESC_H       description_heading of the course
  --s_id S_ID           ID of a student
  --t_id T_ID           ID of a teacher
  --alias ALIAS         The alias
  --t_email T_EMAIL     teacher email
  --inv_role INV_ROLE   role for invitation
```
</details>

<details>

  <summary >Possible_services </summary>
  
 ```python
 
    possible_services = [
        'courses',
        'aliases',
        'announcements',
        'course_work',
        'student_submissions',
        'course_work_materials',
        'students',
        'teachers',
        'topics',
        'invitations',
        'user_profiles'
     ]
   ```
</details>

<details>

  <summary >Possible methods</summary>
  
 ```python
 
    possible_methods = [
        'd_create', #detaild create
        'q_create', #quick create
        'delete', 
        'get',
        'list',
        'd_patch', #detaild patch
        'q_patch', #quick patch
        'modify', 
        'return',
        'accept',
        'tern_in',
        'reclaim'
    ]

```
</details>


- ##### for CONTRIBUTING please contact me :) 









