// Authentication state
let authToken = localStorage.getItem('authToken');
let currentUser = null;

document.addEventListener("DOMContentLoaded", () => {
  const activitiesList = document.getElementById("activities-list");
  const activitySelect = document.getElementById("activity");
  const signupForm = document.getElementById("signup-form");
  const messageDiv = document.getElementById("message");
  
  // Auth elements
  const loginBtn = document.getElementById("login-btn");
  const logoutBtn = document.getElementById("logout-btn");
  const loginModal = document.getElementById("login-modal");
  const loginForm = document.getElementById("login-form");
  const closeModal = document.querySelector(".close");
  const userInfo = document.getElementById("user-info");
  const usernameDisplay = document.getElementById("username-display");
  const loginError = document.getElementById("login-error");

  // Initialize auth state
  checkAuthState();

  // Login modal handlers
  loginBtn.addEventListener("click", () => {
    loginModal.classList.remove("hidden");
  });

  closeModal.addEventListener("click", () => {
    loginModal.classList.add("hidden");
    loginError.classList.add("hidden");
  });

  window.addEventListener("click", (e) => {
    if (e.target === loginModal) {
      loginModal.classList.add("hidden");
      loginError.classList.add("hidden");
    }
  });

  // Login form submission
  loginForm.addEventListener("submit", async (e) => {
    e.preventDefault();
    const username = document.getElementById("username").value;
    const password = document.getElementById("password").value;

    try {
      const response = await fetch("/api/login", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ username, password }),
      });

      if (response.ok) {
        const data = await response.json();
        authToken = data.access_token;
        localStorage.setItem('authToken', authToken);
        currentUser = { username: data.username, role: data.role };
        
        loginModal.classList.add("hidden");
        loginError.classList.add("hidden");
        loginForm.reset();
        updateUIForAuth();
        fetchActivities();
      } else {
        const error = await response.json();
        loginError.textContent = error.detail || "Login failed";
        loginError.classList.remove("hidden");
      }
    } catch (error) {
      loginError.textContent = "Network error. Please try again.";
      loginError.classList.remove("hidden");
    }
  });

  // Logout handler
  logoutBtn.addEventListener("click", () => {
    authToken = null;
    currentUser = null;
    localStorage.removeItem('authToken');
    updateUIForAuth();
    fetchActivities();
  });

  // Check auth state and get user info
  async function checkAuthState() {
    if (authToken) {
      try {
        const response = await fetch("/api/me", {
          headers: { "Authorization": `Bearer ${authToken}` }
        });
        
        if (response.ok) {
          currentUser = await response.json();
          updateUIForAuth();
        } else {
          // Token invalid
          authToken = null;
          localStorage.removeItem('authToken');
          updateUIForAuth();
        }
      } catch (error) {
        console.error("Auth check failed:", error);
      }
    }
    fetchActivities();
  }

  // Update UI based on auth state
  function updateUIForAuth() {
    if (currentUser && currentUser.role === 'teacher') {
      loginBtn.classList.add("hidden");
      userInfo.classList.remove("hidden");
      usernameDisplay.textContent = `👤 ${currentUser.username}`;
      document.querySelectorAll('.teacher-only').forEach(el => el.classList.remove('hidden'));
      document.querySelectorAll('.delete-btn').forEach(btn => btn.style.display = 'inline');
    } else {
      loginBtn.classList.remove("hidden");
      userInfo.classList.add("hidden");
      document.querySelectorAll('.teacher-only').forEach(el => el.classList.add('hidden'));
      document.querySelectorAll('.delete-btn').forEach(btn => btn.style.display = 'none');
    }
  }

  // Function to fetch activities from API
  async function fetchActivities() {
    try {
      const response = await fetch("/activities");
      const activities = await response.json();

      // Clear loading message
      activitiesList.innerHTML = "";
      activitySelect.innerHTML = '<option value="">-- Select an activity --</option>';

      // Populate activities list
      Object.entries(activities).forEach(([name, details]) => {
        const activityCard = document.createElement("div");
        activityCard.className = "activity-card";

        const spotsLeft =
          details.max_participants - details.participants.length;

        // Create participants HTML with delete icons
        const participantsHTML =
          details.participants.length > 0
            ? `<div class="participants-section">
              <h5>Participants:</h5>
              <ul class="participants-list">
                ${details.participants
                  .map(
                    (email) =>
                      `<li><span class="participant-email">${email}</span><button class="delete-btn" data-activity="${name}" data-email="${email}" style="display: ${currentUser?.role === 'teacher' ? 'inline' : 'none'}">❌</button></li>`
                  )
                  .join("")}
              </ul>
            </div>`
            : `<p><em>No participants yet</em></p>`;

        activityCard.innerHTML = `
          <h4>${name}</h4>
          <p>${details.description}</p>
          <p><strong>Schedule:</strong> ${details.schedule}</p>
          <p><strong>Availability:</strong> ${spotsLeft} spots left</p>
          <div class="participants-container">
            ${participantsHTML}
          </div>
        `;

        activitiesList.appendChild(activityCard);

        // Add option to select
        const option = document.createElement("option");
        option.value = name;
        option.textContent = name;
        activitySelect.appendChild(option);
      });

      // Add event listeners to delete buttons
      document.querySelectorAll(".delete-btn").forEach((button) => {
        button.addEventListener("click", handleDelete);
      });
    } catch (error) {
      activitiesList.innerHTML = `<p class="error">Failed to load activities: ${error.message}</p>`;
    }
  }

  // Handle delete button click
  async function handleDelete(e) {
    if (!authToken) {
      showMessage("You must be logged in to remove participants", "error");
      return;
    }

    const activityName = e.target.dataset.activity;
    const email = e.target.dataset.email;

    if (confirm(`Remove ${email} from ${activityName}?`)) {
      try {
        const response = await fetch(
          `/activities/${encodeURIComponent(activityName)}/unregister?email=${encodeURIComponent(email)}`,
          { 
            method: "DELETE",
            headers: { "Authorization": `Bearer ${authToken}` }
          }
        );

        if (response.ok) {
          showMessage("Student removed successfully", "success");
          fetchActivities();
        } else {
          const error = await response.json();
          showMessage(error.detail || "Failed to remove student", "error");
        }
      } catch (error) {
        showMessage(`Error: ${error.message}`, "error");
      }
    }
  }

  // Handle signup form submission
  signupForm.addEventListener("submit", async (e) => {
    e.preventDefault();

    if (!authToken) {
      showMessage("You must be logged in as a teacher to enroll students", "error");
      return;
    }

    const email = document.getElementById("email").value;
    const activityName = document.getElementById("activity").value;

    if (!activityName) {
      showMessage("Please select an activity", "error");
      return;
    }

    try {
      const response = await fetch(
        `/activities/${encodeURIComponent(activityName)}/signup?email=${encodeURIComponent(email)}`,
        { 
          method: "POST",
          headers: { "Authorization": `Bearer ${authToken}` }
        }
      );

      if (response.ok) {
        showMessage("Student signed up successfully!", "success");
        signupForm.reset();
        fetchActivities();
      } else {
        const error = await response.json();
        showMessage(error.detail || "Failed to sign up", "error");
      }
    } catch (error) {
      showMessage(`Error: ${error.message}`, "error");
    }
  });

  // Show message to user
  function showMessage(text, type) {
    messageDiv.textContent = text;
    messageDiv.className = type;
    messageDiv.classList.remove("hidden");

    setTimeout(() => {
      messageDiv.classList.add("hidden");
    }, 5000);
  }
});
