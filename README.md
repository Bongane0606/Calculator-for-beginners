Calculator-for-beginners

So the initial thought is to create a calculator, not the scientific by the ordinary one. The kind that even a 2 year old can use and understand. This is a fun project that helps us in undersatnding how apps or programmes are setup together to make one functional programme, where in tthis case the programme will be a calculator

The logic on for this calculator is for it to be able to do the following :

    Give out correct and accurate results
    Add, Subtract, Divide and Multiply
    Be able to clear out(erase when requested or when an erase button is clicked)
    Have a stylist colour vibe going on

Promote for running the web

Run the application locally:

To start the server binding only to your machine (default):

```bash
./run_student_analysis_web.sh
```

To make the app reachable from other devices on the same network (phone, other
desktop), bind the server to all interfaces and use your machine IP:

```bash
# bind to all interfaces so other devices can connect
./run_student_analysis_web.sh 8030 0.0.0.0

# find your machine IP (example on Linux)
hostname -I
# then open on the other device: http://<YOUR_MACHINE_IP>:8030/
```

Access the Application (clickable locally):
[Open Web App](http://localhost:8030/)

If you need public access over the internet, use a tunneling service such as
`ngrok` or `localtunnel` and expose port `8030`.
Authors / Developers

    Lebogang Nare
    Ntsako Ngobeni
    Letsoenyo Bongane
