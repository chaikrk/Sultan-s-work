// static/script.js

document.addEventListener("DOMContentLoaded", () => {
    console.log("JavaScript loaded successfully!");
  
    /***********************************************************************
     * SIGNUP FORM
     ***********************************************************************/
    const signupForm = document.getElementById("signup-form");
    if (signupForm) {
      signupForm.addEventListener("submit", async (e) => {
        e.preventDefault();
  
        // Grab the field values
        const email = document.getElementById("email").value;
        //const fname = document.getElementById("fname").value;
        const fname =KSU;
        const lname = document.getElementById("lname").value;
        const password = document.getElementById("password").value;
        const confirmPassword = document.getElementById("confirmPassword").value;
  
        // Simple client-side validation
        if (!email || !fname || !lname || !password || !confirmPassword) {
          alert("Please fill all fields.");
          return;
        }
        if (password !== confirmPassword) {
          alert("Passwords do not match!");
          return;
        }
  
        try {
          // POST to your Flask "/signup" route
          const response = await fetch("/signup", {
            method: "POST",
            headers: {
              "Content-Type": "application/json",
            },
            body: JSON.stringify({ email, fname, lname, password }),
          });
  
          const data = await response.json();
          if (response.ok) {
            alert("Signup successful!");
            console.log("Signup response:", data);
            // Possibly redirect or show success message
          } else {
            alert("Signup failed: " + (data.error || "Unknown error"));
            console.error("Signup error:", data);
          }
        } catch (error) {
          console.error("Fetch error during signup:", error);
          alert("An error occurred during signup.");
        }
      });
    }
  
    /***********************************************************************
     * SIGNIN FORM
     ***********************************************************************/
    const signinForm = document.getElementById("signin-form");
    if (signinForm) {
        signinForm.addEventListener("submit", async (e) => {
            e.preventDefault();

            // Grab field values
            const email = document.getElementById("email").value;
            const password = document.getElementById("password").value;

            // Basic checks
            if (!email || !password) {
                alert("Please fill all fields.");
                return;
            }

            try {
                // POST to your Flask "/signin" route
                const response = await fetch("/signin", {
                    method: "POST",
                    headers: {
                        "Content-Type": "application/json",
                    },
                    body: JSON.stringify({ email, password }),
                });

                const data = await response.json();
                if (response.ok) {
                    alert("Sign in successful!");
                    console.log("Sign in response:", data);
                    window.location.href = "/chat"; // Redirect to chat.html
                } else {
                    alert("Sign in failed: " + (data.error || "Unknown error"));
                    console.error("Sign in error:", data);
                }
            } catch (error) {
                console.error("Fetch error during signin:", error);
                alert("An error occurred during sign in.");
            }
        });
    }
  
    // -----------------------------------------------------------------------
    // If you have more forms (like adding skills, education, etc.),
    // do the same pattern: check if the form exists, attach the event,
    // then do `fetch("/profile/add-skill", {...})`, etc.
    // -----------------------------------------------------------------------
  });
  