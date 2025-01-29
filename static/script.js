document.addEventListener('DOMContentLoaded', function () {
    console.log("JavaScript loaded successfully!");

    // Navigation menu toggle for mobile
    const navToggle = document.querySelector('.nav-toggle');
    const navLinks = document.querySelector('.nav-links');

    if (navToggle && navLinks) {
        navToggle.addEventListener('click', () => {
            navLinks.classList.toggle('active');
        });
    }

    // Form submission handling for all forms
    const forms = document.querySelectorAll('form');
    forms.forEach(form => {
        form.addEventListener('submit', (e) => {
            e.preventDefault();
            console.log(`Form submitted: ${form.id}`);
        });
    });

    // Signup form handling
    const signupForm = document.getElementById('signup-form');
    if (signupForm) {
        signupForm.addEventListener('submit', async (event) => {
            event.preventDefault();

            const fullName = document.getElementById('name').value.trim();
            const email = document.getElementById('email').value.trim();
            const password = document.getElementById('password').value.trim();
            const confirmPassword = document.getElementById('confirm-password').value.trim();

            const [fname, lname = ""] = fullName.split(" ", 2);

            if (password !== confirmPassword) {
                alert("Passwords do not match!");
                return;
            }

            try {
                const response = await fetch('http://127.0.0.1:5000/auth/signup', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ email, fname, lname, password }),
                });

                const data = await response.json();

                if (response.ok) {
                    alert(data.message);
                    localStorage.setItem('email', email);
                    window.location.href = "portfolio.html";
                } else {
                    alert(data.error || "Something went wrong!");
                }
            } catch (error) {
                console.error("Error during signup:", error);
                alert("Failed to register user.");
            }
        });
    }

    // Sign-in form handling
    const signinForm = document.getElementById('signin-form');
    if (signinForm) {
        signinForm.addEventListener('submit', async (event) => {
            event.preventDefault();

            const email = document.getElementById('email').value.trim();
            const password = document.getElementById('password').value.trim();

            try {
                const response = await fetch('http://127.0.0.1:5000/auth/signin', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ email, password }),
                });

                const data = await response.json();

                if (response.ok) {
                    alert(data.message);
                    localStorage.setItem('email', email);
                    window.location.href = "chat.html";
                } else {
                    alert(data.error || "Invalid login credentials!");
                }
            } catch (error) {
                console.error("Error:", error);
                alert("Failed to sign in. Please try again.");
            }
        });
    }

    // Portfolio tab navigation and form handling
    const buttons = document.querySelectorAll('.nav-button');
    const sections = document.querySelectorAll('.form-section');

    buttons.forEach(button => {
        button.addEventListener('click', () => {
            const target = button.dataset.target;
            sections.forEach(section => section.classList.remove('active'));
            document.getElementById(target).classList.add('active');
            buttons.forEach(btn => btn.classList.remove('active'));
            button.classList.add('active');
        });
    });

    // Handle adding education
    document.getElementById('education-form').addEventListener('submit', async (event) => {
        event.preventDefault();
        await handleSubmit('education', 'profile/add-education');
    });

    // Handle adding experience
    document.getElementById('experience-form').addEventListener('submit', async (event) => {
        event.preventDefault();
        await handleSubmit('experience', 'profile/add-experience');
    });

    // Handle adding certification
    document.getElementById('certification-form').addEventListener('submit', async (event) => {
        event.preventDefault();
        await handleSubmit('certification', 'profile/add-certification');
    });

    // Handle adding skill
    document.getElementById('skill-form').addEventListener('submit', async (event) => {
        event.preventDefault();
        await handleSubmit('skill', 'profile/add-skill');
    });

    async function handleSubmit(section, endpoint) {
        const email = localStorage.getItem('email');
        const formData = new FormData(document.getElementById(`${section}-form`));
        const data = Object.fromEntries(formData.entries());
        data.email = email;

        if (!email || Object.values(data).some(value => !value.trim())) {
            alert("All fields are required.");
            return;
        }

        try {
            const response = await fetch(`http://127.0.0.1:5000/${endpoint}`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(data),
            });

            const result = await response.json();

            if (response.ok) {
                alert(result.message);
                loadData(section);
            } else {
                alert(result.error || `Failed to add ${section}.`);
            }
        } catch (error) {
            console.error(`Error adding ${section}:`, error);
            alert(`Failed to add ${section}.`);
        }
    }

    async function loadData(section) {
        const email = localStorage.getItem('email');
        if (!email) {
            console.error("No email found in localStorage.");
            return;
        }

       /* try {
            const response = await fetch(`http://127.0.0.1:5000/profile/get-${section}?email=${email}`);

            if (!response.ok) {
                throw new Error(`Failed to fetch ${section} entries.`);
            }

            const entries = await response.json();
            const list = document.getElementById(`${section}-list`);
            list.innerHTML = '';

            entries.forEach((entry, index) => {
                const item = document.createElement('div');
                item.className = 'added-item';
                item.innerHTML = `
                    ${Object.entries(entry).map(([key, value]) => `<p><strong>${key}:</strong> ${value}</p>`).join('')}
                    <button onclick="deleteItem('${section}', ${entry.id})">Delete</button>
                `;
                list.appendChild(item);
            });
        } catch (error) {
            console.error(`Error loading ${section} entries:`, error);
        }*/
    }

    async function deleteItem(section, id) {
        try {
            const response = await fetch(`http://127.0.0.1:5000/profile/delete-${section}?id=${id}`, {
                method: 'DELETE',
            });

            const result = await response.json();

            if (response.ok) {
                alert(result.message);
                loadData(section);
            } else {
                alert(result.error || `Failed to delete ${section}.`);
            }
        } catch (error) {
            console.error(`Error deleting ${section}:`, error);
            alert(`Failed to delete ${section}.`);
        }
    }

    // Load data for all sections on page load
    ['education', 'experience', 'certification', 'skill'].forEach(loadData);

    const skillLevelInput = document.getElementById('skill_level');
    const skillLevelValue = document.querySelector('.range-value');
    skillLevelInput.addEventListener('input', function () {
        skillLevelValue.textContent = this.value;
    });

});
document.addEventListener('DOMContentLoaded', function () {
    const chatButton = document.getElementById('continue-chat');
    if (chatButton) {
        chatButton.addEventListener('click', function () {
            window.location.href = "chat.html";
        });
    }
});

