// -------- STATE --------
let currentUser = null;

// -------- AUTH --------
function handleLogin() {
  const email = document.getElementById('login-email').value.trim();
  const password = document.getElementById('login-password').value.trim();
  const errorEl = document.getElementById('login-error');

  if (!email || !password) {
    errorEl.textContent = "Please enter email and password.";
    return;
  }

  fetch('/login', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ email, password })
  })
  .then(res => res.json())
  .then(data => {
    if (data.status === 'success') {
      currentUser = data.email;
      document.getElementById('nav-email').textContent = currentUser;
      document.getElementById('main-nav').style.display = 'flex';
      showPage('home');
    } else {
      errorEl.textContent = data.message;
    }
  })
  .catch(() => errorEl.textContent = "Could not connect to server.");
}

function handleRegister() {
  const email = document.getElementById('reg-email').value.trim();
  const password = document.getElementById('reg-password').value.trim();
  const confirm = document.getElementById('reg-confirm').value.trim();
  const errorEl = document.getElementById('reg-error');
  const successEl = document.getElementById('reg-success');

  errorEl.textContent = '';
  successEl.textContent = '';

  if (!email || !password || !confirm) {
    errorEl.textContent = "All fields are required.";
    return;
  }

  if (password !== confirm) {
    errorEl.textContent = "Passwords do not match.";
    return;
  }

  fetch('/register', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ email, password })
  })
  .then(res => res.json())
  .then(data => {
    if (data.status === 'success') {
      successEl.textContent = "Registered successfully! Please login.";
      setTimeout(() => showLogin(), 1500);
    } else {
      errorEl.textContent = data.message;
    }
  })
  .catch(() => errorEl.textContent = "Could not connect to server.");
}

function handleLogout() {
  fetch('/logout', { method: 'POST' })
  .then(() => {
    currentUser = null;
    document.getElementById('main-nav').style.display = 'none';
    document.querySelectorAll('.page').forEach(p => p.classList.remove('active'));
    document.getElementById('page-auth').classList.add('active');
    document.getElementById('login-email').value = '';
    document.getElementById('login-password').value = '';
    document.getElementById('login-error').textContent = '';
    showLogin();
  });
}

function showLogin() {
  document.getElementById('login-form').style.display = 'block';
  document.getElementById('register-form').style.display = 'none';
}

function showRegister() {
  document.getElementById('login-form').style.display = 'none';
  document.getElementById('register-form').style.display = 'block';
}

// -------- PAGE ROUTING --------
function showPage(id) {
  document.querySelectorAll('.page').forEach(p => p.classList.remove('active'));
  document.querySelectorAll('.nav-links a').forEach(a => a.classList.remove('active'));
  const pg = document.getElementById('page-' + id);
  if (pg) pg.classList.add('active');
  const navIdx = { home: 0, exercises: 1, contact: 2 };
  const navLinks = document.querySelectorAll('.nav-links a');
  if (navIdx[id] !== undefined) navLinks[navIdx[id]].classList.add('active');
  window.scrollTo({ top: 0, behavior: 'smooth' });
}

// -------- MODAL DATA --------
const exercises = {
  lunges:{icon:'🦵',name:'Lunges',desc:'A foundational lower-body movement that restores strength, balance, and neuromuscular control post-injury.',steps:['Stand tall with feet hip-width apart, hands on hips.','Step one foot forward about 60–70 cm, lowering your back knee.','Keep your front knee above your ankle — do not let it go past your toes.','Push through your front heel to return to starting position.','Alternate legs for 10–15 reps each side.']},
  sitstand:{icon:'🪑',name:'Sit to Stand',desc:'Simulates a critical daily movement pattern, rebuilding confidence and lower-limb power after surgery or injury.',steps:['Sit at the edge of a sturdy chair, feet shoulder-width apart.','Lean slightly forward — "nose over toes" — without rounding your back.','Press through your heels and straighten legs to stand.','Slowly lower back down with control — do not plop back.','Repeat 8–12 times. Use armrests for support if needed.']},
  stepup:{icon:'🪜',name:'Step Ups',desc:'Improves single-leg strength and coordination, essential for stairs and uneven terrain after rehabilitation.',steps:['Stand facing a step or low platform (15–25 cm high).','Place one entire foot on the step — heel included.','Drive through the top foot to step up and bring the other foot alongside.','Slowly lower the trailing foot back to the ground.','Complete 10 reps on each leg. Focus on control, not speed.']},
  knee:{icon:'🦿',name:'Knee Extension',desc:'Directly targets the quadriceps to rebuild strength and support the knee joint after surgery or prolonged immobilisation.',steps:['Sit in a chair with your back straight, thighs fully supported.','Loop a resistance band around your ankle or use a machine if available.','Slowly extend the knee until the leg is almost straight.','Hold at the top for 2 seconds — squeeze the quadriceps.','Lower slowly over 3 seconds. Repeat 15 times per leg.']},
  squats:{icon:'🏋️',name:'Squats',desc:'The king of lower-body rehabilitation movements, rebuilding functional strength from the ground up.',steps:['Stand with feet shoulder-width apart, toes slightly turned out.','Engage your core and push your hips back as if sitting into a chair.','Lower until thighs are parallel to the ground (or as comfortable).','Keep chest lifted, knees tracking over second toe.','Drive through heels to return to standing. Do 12–15 reps.']},
  walking:{icon:'🚶',name:'Walking Tracker',desc:'Structured walking is one of the most powerful and underrated rehabilitation tools.',steps:['Start with a comfortable, achievable distance (e.g. 1,000 steps).','Maintain an upright posture — head up, shoulders back.','Swing arms naturally and land on the heel, rolling through to the toe.','Increase daily step count by 10% each week to avoid overload.','Track your steps, pace, and any pain levels in your progress log.']}
};

function openModal(key) {
  const ex = exercises[key];
  if (!ex) return;

  const choiceMap = {
    knee: '1', squats: '2', sitstand: '3', stepup: '4', lunges: '5', walking: '6'
  };

  const steps = ex.steps.map((s, i) =>
    `<li><div class="step-num">${i + 1}</div><span>${s}</span></li>`
  ).join('');

  document.getElementById('modal-body').innerHTML = `
    <div class="modal-icon">${ex.icon}</div>
    <h2>${ex.name}</h2>
    <p>${ex.desc}</p>
    <ul class="modal-steps">${steps}</ul>
  `;

  const choice = choiceMap[key] || null;
  const closeBtn = document.querySelector('.modal-close');

  if (choice) {
    closeBtn.textContent = 'Select & Start Exercise →';
    closeBtn.onclick = () => selectAndStart(choice);
  } else {
    closeBtn.textContent = 'Close';
    closeBtn.onclick = closeModal;
  }

  document.getElementById('modal').classList.add('open');
  document.body.style.overflow = 'hidden';
}

function selectAndStart(choice) {
  fetch('/select_exercise', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ choice: choice, email: currentUser })
  })
  .then(res => res.json())
  .then(data => {
    alert('Starting: ' + data.exercise);
    closeModal();
  })
  .catch(err => {
    alert('Could not connect to backend. Is Flask running?');
    console.error(err);
  });
}

function closeModal() {
  document.getElementById('modal').classList.remove('open');
  document.body.style.overflow = '';
}

function closeModalBg(e) {
  if (e.target === document.getElementById('modal')) closeModal();
}

// -------- PROGRESS --------
function viewProgress(exerciseType) {
  if (!currentUser) {
    alert('Please login first.');
    return;
  }
  const url = `/progress/${exerciseType}/${currentUser}`;
  window.open(url, '_blank');
}

// -------- CONTACT FORM --------
function submitForm() {
  document.getElementById('form-container').style.display = 'none';
  document.getElementById('form-success').classList.add('show');
}

function resetForm() {
  document.getElementById('form-container').style.display = 'block';
  document.getElementById('form-success').classList.remove('show');
}