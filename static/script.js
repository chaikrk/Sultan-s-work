// Initialize select2 for the new dropdown menus
$(document).ready(function() {
    $('#degree_search').select2({
      placeholder: "Search for a degree...",
      allowClear: true
    });
    $('#major_search').select2({
      placeholder: "Search for a major...",
      allowClear: true
    });
    $('#university_search').select2({
      placeholder: "Search for a university...",
      allowClear: true
    });
    $('#country_search').select2({
      placeholder: "Search for a country...",
      allowClear: true
    });
  });
  
async function loadData(section) {
    const list = document.getElementById(`${section}-list`);
    // If we're not on the portfolio page, `list` will be null
    if (!list) {
        return; // Just skip the rest if the element doesn't exist
    }
    const email = localStorage.getItem("email");
    if (!email) {
        console.error("No email found in localStorage.");
        return;
    }

    try {
        const response = await fetch(`/profile/get-${section}?email=${email}`);
        if (!response.ok) throw new Error(`Failed to fetch ${section} entries.`);

        const entries = await response.json();
        const list = document.getElementById(`${section}-list`);
        list.innerHTML = "";

        entries.forEach((entry) => {
            // Destructure `id` from entry, and group the rest into `fields`
            const { id, ...fields } = entry;
          
            const item = document.createElement("div");
            item.className = "added-item";
          
            // Build the display HTML from the remaining fields (no `id`)
            const detailsHTML = Object.entries(fields)
              .map(([key, value]) => `<p><strong>${key}:</strong> ${value}</p>`)
              .join("");
          
            // Include the Delete button, passing the `id` to deleteItem()
            item.innerHTML = `
              ${detailsHTML}
              <button onclick="deleteItem('${section}', ${id})">Delete</button>
            `;
          
            // Finally, append to your container
            list.appendChild(item);
          });
    } catch (error) {
        console.error(`Error loading ${section} entries:`, error);
    }
}

async function deleteItem(section, id) {
    try {
        const response = await fetch(`/profile/delete-${section}?id=${id}`, {
            method: "DELETE",
        });

        const result = await response.json();

        if (response.ok) {
            alert(`${section} deleted successfully!`);
            loadData(section);
        } else {
            alert(`Failed to delete ${section}: ${result.error}`);
        }
    } catch (error) {
        console.error(`Error deleting ${section}:`, error);
        alert(`Failed to delete ${section}.`);
    }
}

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
            const fullName = document.getElementById("name").value.trim();
            const email = document.getElementById("email").value;
            const password = document.getElementById("password").value;
            const confirmPassword = document.getElementById("confirm-password").value;

            // Split full name into first and last name
            let [fname, ...lnameParts] = fullName.split(" ");
            let lname = lnameParts.join(" ") || "N/A";  // If lname is empty, set it to "N/A"

            // Simple client-side validation
            if (!email || !fname || !password || !confirmPassword) {
                alert("Please fill all fields.");
                return;
            }
            if (password !== confirmPassword) {
                alert("Passwords do not match!");
                return;
            }

            try {
                // POST to your Flask "/signup" route
                const response = await fetch("/auth/signup", {
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
                    localStorage.setItem("email", email);  // Store email for portfolio
                    window.location.href = "/portfolio";  // Redirect to portfolio
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

            const email = document.getElementById("email").value;
            const password = document.getElementById("password").value;

            if (!email || !password) {
                alert("Please fill all fields.");
                return;
            }

            try {
                const response = await fetch("/auth/signin", {
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
                    localStorage.setItem("email", email);  // Store email for portfolio
                    window.location.href = "/chat";  // Redirect to chat
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

    /***********************************************************************
     * PORTFOLIO FORM HANDLING
     ***********************************************************************/
    const sections = ["education", "experience", "certification", "skill"];
    sections.forEach((section) => {
        const form = document.getElementById(`${section}-form`);
        if (form) {
            form.addEventListener("submit", async (e) => {
                e.preventDefault();
                await handleSubmit(section, `/profile/add-${section}`);
            });
        }
    });

    async function handleSubmit(section, endpoint) {
        const email = localStorage.getItem("email");
        if (!email) {
            alert("User not found. Please log in again.");
            return;
        }

        const formData = new FormData(document.getElementById(`${section}-form`));
        const data = Object.fromEntries(formData.entries());
        data.email = email;

        if (Object.values(data).some(value => !value.trim())) {
            alert("All fields are required.");
            return;
        }

        try {
            const response = await fetch(endpoint, {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify(data),
            });

            const result = await response.json();

            if (response.ok) {
                alert(`${section} added successfully!`);
                loadData(section);
            } else {
                alert(`Failed to add ${section}: ${result.error}`);
            }
        } catch (error) {
            console.error(`Error adding ${section}:`, error);
            alert(`Failed to add ${section}.`);
        }
    }

    
    // ---------------------------------------------------------------------
    /*async function fetchUserPortfolio() {
        const email = localStorage.getItem("email");  // Retrieve stored email
        if (!email) {
            console.error("User email not found in localStorage.");
            return;
        }
    
        try {
            const response = await fetch(`/profile/get-user-portfolio?email=${encodeURIComponent(email)}`);
            const data = await response.json();
    
            if (response.ok) {
                console.log("User portfolio retrieved:", data);
                displayUserPortfolio(data);  // Call function to update UI
            } else {
                console.warn("User portfolio not found:", data.error);
            }
        } catch (error) {
            console.error("Error fetching user portfolio:", error);
        }
    }*/
    // ------------------------------------------------------------------
   
    

    // Load data for all portfolio sections on page load
    sections.forEach(loadData);

    /***********************************************************************
     * NAVIGATION HANDLING
     ***********************************************************************/
    const chatButton = document.getElementById("continue-chat");
    if (chatButton) {
        chatButton.addEventListener("click", () => {
            window.location.href = "/chat";
        });
    }

    const buttons = document.querySelectorAll(".nav-button");
    const contentSections = document.querySelectorAll(".form-section");

    buttons.forEach((button) => {
        button.addEventListener("click", () => {
            const target = button.dataset.target;
            contentSections.forEach((section) => section.classList.remove("active"));
            document.getElementById(target).classList.add("active");
            buttons.forEach((btn) => btn.classList.remove("active"));
            button.classList.add("active");
        });
    });
});
