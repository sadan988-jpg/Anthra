const API = 'http://127.0.0.1:8000';

// ─── Toast ───────────────────────────────────────────────
function showToast(msg, type='info'){
  const t = document.getElementById('toast');
  t.textContent = msg; t.className = `toast ${type} show`;
  setTimeout(()=> t.classList.remove('show'), 3500);
}

// ─── Doctor Auth ──────────────────────────────────────────
async function doctorLogin(){
  const email   = document.getElementById('doc-login-email').value.trim();
  const license = document.getElementById('doc-login-license').value.trim();
  if(!email||!license) return showToast('Please fill all fields','error');

  const res = await fetch(`${API}/login/doctor`, {
    method:'POST', headers:{'Content-Type':'application/json'},
    body: JSON.stringify({email, license_number: license})
  });
  if(!res.ok){ showToast('Doctor not found or not approved','error'); return; }
  const doc = await res.json();
  sessionStorage.setItem('doctor', JSON.stringify(doc));
  window.location.href = 'doctor.html';
}

async function doctorRegister(){
  const body = {
    name: document.getElementById('doc-reg-name').value,
    email: document.getElementById('doc-reg-email').value,
    license_number: document.getElementById('doc-reg-license').value,
    specialization: document.getElementById('doc-reg-spec').value
  };
  if(!body.name||!body.email) return showToast('Fill all fields','error');
  const res = await fetch(`${API}/register/doctor`,{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify(body)});
  if(res.ok){ showToast('Registered! Awaiting admin approval ✓','success'); }
  else { const e=await res.json(); showToast(e.detail||'Error','error'); }
}

// ─── Patient Auth ─────────────────────────────────────────
async function patientLogin(){
  const mobile = document.getElementById('pat-login-mobile').value.trim();
  if(!mobile) return showToast('Enter mobile number','error');
  const res = await fetch(`${API}/patient/dashboard/${mobile}`);
  if(!res.ok||res.status===404){ showToast('Patient not found','error'); return; }
  const data = await res.json();
  if(data.error){ showToast('Patient not found','error'); return; }
  sessionStorage.setItem('patient', JSON.stringify(data.patient));
  window.location.href = 'patient.html';
}

async function patientRegister(){
  const body = {
    name: document.getElementById('pat-reg-name').value,
    mobile: document.getElementById('pat-reg-mobile').value,
    dob: document.getElementById('pat-reg-dob').value,
    gender: document.getElementById('pat-reg-gender').value,
    pincode: document.getElementById('pat-reg-pincode').value,
    genetic_history: document.getElementById('pat-reg-genetic').value,
    habits: document.getElementById('pat-reg-habits').value
  };
  if(!body.name || !body.mobile) return showToast('Fill all required fields','error');
  
  const res = await fetch(`${API}/register/patient`, {
    method:'POST',
    headers:{'Content-Type':'application/json'},
    body:JSON.stringify(body)
  });
  
  if(res.ok){
    const data = await res.json();
    // SHOW THE ID CLEARLY IN A POPUP
    alert(`🎉 Registration Successful!\n\nYour Patient ID is: ${data.id}\nYour Mobile: ${body.mobile}\n\nUse this ID in the Doctor Portal to "Push" notifications.`);
    showToast(`Registered! ID: ${data.id}`,'success');
    switchAuthTab('patient','login'); // Switch to login tab automatically
  } else {
    const e = await res.json();
    showToast(e.detail || 'Error','error');
  }
}
