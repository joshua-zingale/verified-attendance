# Verified Attendance

Verified Attendance is a lightweight web server for collecting attendance in a university setting,
created for use in a lab section that I am teaching at the University of California Riverside.
I have made the program to be easily deployable for use by anyone who wants to log attendance.

The purpose of Verified Attendance is to track attendance in a way that one could only be marked as in attendance if he actually attended the lecture. The following is the workflow:

1. The admin (instructor) generates unique codes from the admin portal.
2. The admin opens the form for submission from the admin portal.
3. The admin prints out the codes and distributes (or otherwise distributes) one code to each student who attends the lecture.
    - I do this by using the "Print Codes" button to get a printout of the codes. Then, I hand out one code to each student who enters the lecture room.
4. Students fill out the attendance form by inputting their student information alongside a code.
    - A code is required for submission and can only be used once, preventing sharing.
5. After attendance has been taken, the admin may close the form, download the attendance, and reset the codes/attendance for the next class.

At any time, the admin can open and close the attendance form, generate more codes, delete all of the codes, download a CSV file of the attendance, or reset the attendance.

## Setup

[Docker](https://www.docker.com/) is the easiest way to get this web server up and running.
The following instructions will assume that Docker is already installed on your deployment machine.


### Cloning Repository

First, you must clone this repository to your machine with

```bash

git clone https://github.com/joshua-zingale/verified-attendance.git
```

After cloning the repository, enter its root directory.


### Running with Docker

There are two environment variables that must be set for this application.


| Name     | Value   |
| -------- | ------- |
| VERIFIED_ATTENDANCE_PORT  | The port to which the web server should broadcast. e.g. "80" or "8000"  |
| ADMIN_PASSWORD | The password to access the admin portal. |

After setting these two variables, you can launch the web server by running the following from the root directory of the repository:

```bash
docker compose up
```

In unix-like shells, you can set these variables like so:

```bash
VERIFIED_ATTENDANCE_PORT="80" ADMIN_PASSWORD="you_should_change_this" docker compose up
```

## Accessing the Application

Once the server is running, you can access the application through your web browser:

* **Student Portal:** `http://localhost:<VERIFIED_ATTENDANCE_PORT>/`
* **Instructor Portal:** `http://localhost:<VERIFIED_ATTENDANCE_PORT>/admin` (You will be prompted for the `ADMIN_PASSWORD`.)

Replace `<VERIFIED_ATTENDANCE_PORT>` with the port number you set in the environment variable.

### Setting Up Remote Access

You almost certainly want to allow those filling out the attendance form to access the website from their devices. To do this, you will either need to install the web server on a machine that is being forwarded through a router or you will need an IP tunnelling service.

In my case, I do not have access to any port-forwarded machines at my university, so I set up the web server on a lab computer and used the free static IP from [ngrok](https://ngrok.com/) to tunnel my locally hosted application to the world.

## Application Images
### Closed Attendance Form

![Closed Attendance Form](images/attendance-not-being-taken.png)

### Filled Out Attendance Form
![Filled Out Attendance Form](images/filled-out-form.png)

### Administrator Portal
![Administrator Portal](images/admin-portal.png)
