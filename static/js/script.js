/**
 * Jalan Sales — FINAL PREMIUM JS
 * Ultra Smooth UI Interactions
 */

document.addEventListener('DOMContentLoaded', () => {

  /* ─────────────────────────────────────────────
     FLASH AUTO REMOVE
  ───────────────────────────────────────────── */

  const flashMessages = document.querySelectorAll('.flash-msg');

  flashMessages.forEach((msg, index) => {

    setTimeout(() => {

      msg.style.opacity = '0';
      msg.style.transform = 'translateX(60px)';

      setTimeout(() => {
        msg.remove();
      }, 400);

    }, 4500 + (index * 300));

  });

  /* ─────────────────────────────────────────────
     PHONE VALIDATION
  ───────────────────────────────────────────── */

  const phoneInputs = document.querySelectorAll('input[type="tel"]');

  phoneInputs.forEach(input => {

    input.addEventListener('input', () => {

      input.value = input.value
        .replace(/\D/g, '')
        .slice(0, 15);

    });

  });

  /* ─────────────────────────────────────────────
     LOGIN FORM
  ───────────────────────────────────────────── */

  const loginForm = document.getElementById('loginForm');

  if (loginForm) {

    loginForm.addEventListener('submit', (e) => {

      const name = document.getElementById('name').value.trim();

      const phone = document.getElementById('phone').value.trim();

      const btn = loginForm.querySelector('[type="submit"]');

      removeErrors();

      if (!name || !phone) {

        e.preventDefault();

        shake(loginForm);

        if (!name) {
          showError('name', 'Please enter your name');
        }

        if (!phone) {
          showError('phone', 'Please enter your mobile number');
        }

        return;
      }

      if (!/^\d{10,15}$/.test(phone)) {

        e.preventDefault();

        shake(loginForm);

        showError('phone', 'Enter valid mobile number');

        return;
      }

      btn.disabled = true;

      btn.innerHTML = `
        <span class="spinner"></span>
        Entering...
      `;

    });

  }

  /* ─────────────────────────────────────────────
     SCAN BUTTON PROTECTION
  ───────────────────────────────────────────── */

  const scanBtn = document.getElementById('scanBtn');

  if (scanBtn) {

    scanBtn.addEventListener('click', () => {

      scanBtn.style.pointerEvents = 'none';

      scanBtn.innerHTML = `
        <span class="spinner"></span>
        Sending Request...
      `;

    });

  }

  /* ─────────────────────────────────────────────
     VISIT COUNTER ANIMATION
  ───────────────────────────────────────────── */

  const visitNumber = document.querySelector('.visit-number');

  if (visitNumber) {

    const finalCount = parseInt(
      visitNumber.dataset.count || 0
    );

    animateCounter(
      visitNumber,
      0,
      finalCount,
      1200
    );

  }

  function animateCounter(el, start, end, duration) {

    let startTime = null;

    function update(currentTime) {

      if (!startTime) {
        startTime = currentTime;
      }

      const progress = Math.min(
        (currentTime - startTime) / duration,
        1
      );

      const easeOut = 1 - Math.pow(1 - progress, 4);

      el.textContent = Math.floor(
        easeOut * (end - start) + start
      );

      if (progress < 1) {

        requestAnimationFrame(update);

      } else {

        el.textContent = end;

      }

    }

    requestAnimationFrame(update);

  }

  /* ─────────────────────────────────────────────
     PROGRESS BAR ANIMATION
  ───────────────────────────────────────────── */

  const progressFill = document.getElementById('progressFill');

  if (progressFill) {

    const target = parseInt(
      progressFill.dataset.target || 0
    );

    progressFill.style.width = '0%';

    setTimeout(() => {

      progressFill.style.width = target + '%';

    }, 350);

  }

  /* ─────────────────────────────────────────────
     REWARD POPUP
  ───────────────────────────────────────────── */

  const rewardPopup = document.getElementById('rewardPopup');

  if (rewardPopup) {

    launchConfetti();

    setTimeout(() => {
      closeRewardPopup();
    }, 7000);

    rewardPopup.addEventListener('click', (e) => {

      if (e.target.id === 'rewardPopup') {
        closeRewardPopup();
      }

    });

  }

  /* ─────────────────────────────────────────────
     ADMIN SEARCH
  ───────────────────────────────────────────── */

  const adminSearch = document.getElementById('adminSearch');

  if (adminSearch) {

    let timeout;

    adminSearch.addEventListener('input', () => {

      clearTimeout(timeout);

      timeout = setTimeout(() => {

        const q = adminSearch.value.trim();

        window.location.href =
          `/admin?q=${encodeURIComponent(q)}`;

      }, 500);

    });

  }

  /* ─────────────────────────────────────────────
     RESET CONFIRMATION
  ───────────────────────────────────────────── */

  document.querySelectorAll('.confirm-reset')
    .forEach(btn => {

      btn.addEventListener('click', (e) => {

        const confirmReset = confirm(
          'Reset all visits & rewards for this customer?'
        );

        if (!confirmReset) {
          e.preventDefault();
        }

      });

    });

  /* ─────────────────────────────────────────────
     COPY QR URL
  ───────────────────────────────────────────── */

  const copyQrBtn = document.getElementById('copyQrUrl');

  if (copyQrBtn) {

    copyQrBtn.addEventListener('click', async () => {

      const url = copyQrBtn.dataset.url;

      try {

        await navigator.clipboard.writeText(url);

        copyQrBtn.innerHTML = '✅ Copied';

        setTimeout(() => {

          copyQrBtn.innerHTML = '📋 Copy Scan URL';

        }, 2200);

      } catch {

        alert('Unable to copy URL');

      }

    });

  }

  /* ─────────────────────────────────────────────
     PARALLAX EFFECT
  ───────────────────────────────────────────── */

  document.addEventListener('mousemove', (e) => {

    const cards = document.querySelectorAll('.glass-card');

    const x = (window.innerWidth / 2 - e.clientX) / 35;

    const y = (window.innerHeight / 2 - e.clientY) / 35;

    cards.forEach(card => {

      card.style.transform =
        `rotateY(${x}deg) rotateX(${-y}deg)`;

    });

  });

  document.addEventListener('mouseleave', () => {

    document.querySelectorAll('.glass-card')
      .forEach(card => {

        card.style.transform = 'rotateY(0deg) rotateX(0deg)';

      });

  });

});

/* ─────────────────────────────────────────────
   HELPERS
───────────────────────────────────────────── */

function shake(element) {

  element.classList.add('shake');

  setTimeout(() => {

    element.classList.remove('shake');

  }, 500);

}

function showError(fieldId, message) {

  const field = document.getElementById(fieldId);

  if (!field) return;

  const error = document.createElement('p');

  error.className = 'input-error';

  error.innerText = message;

  field.parentNode.appendChild(error);

}

function removeErrors() {

  document.querySelectorAll('.input-error')
    .forEach(el => el.remove());

}

/* ─────────────────────────────────────────────
   CLOSE REWARD POPUP
───────────────────────────────────────────── */

function closeRewardPopup() {

  const popup = document.getElementById('rewardPopup');

  if (!popup) return;

  popup.classList.add('hide');

  setTimeout(() => {

    popup.remove();

  }, 400);

}

/* ─────────────────────────────────────────────
   MINI CONFETTI
───────────────────────────────────────────── */

function launchConfetti() {

  for (let i = 0; i < 50; i++) {

    const confetti = document.createElement('div');

    confetti.className = 'confetti-piece';

    confetti.style.left = Math.random() * 100 + 'vw';

    confetti.style.animationDuration =
      (Math.random() * 3 + 2) + 's';

    confetti.style.opacity = Math.random();

    confetti.style.transform =
      `rotate(${Math.random() * 360}deg)`;

    document.body.appendChild(confetti);

    setTimeout(() => {

      confetti.remove();

    }, 5000);

  }

}

/* ─────────────────────────────────────────────
   EXTRA STYLES
───────────────────────────────────────────── */

const style = document.createElement('style');

style.innerHTML = `

.spinner{
  width:14px;
  height:14px;
  border:2px solid rgba(0,0,0,.2);
  border-top-color:#111;
  border-radius:50%;
  display:inline-block;
  animation:spin .6s linear infinite;
}

@keyframes spin{
  to{
    transform:rotate(360deg);
  }
}

.shake{
  animation:shake .4s ease;
}

@keyframes shake{
  0%,100%{
    transform:translateX(0);
  }
  20%,60%{
    transform:translateX(-8px);
  }
  40%,80%{
    transform:translateX(8px);
  }
}

.input-error{
  color:#f87171;
  font-size:.78rem;
  margin-top:5px;
}

.confetti-piece{
  position:fixed;
  top:-10px;
  width:10px;
  height:10px;
  background:#f6c90e;
  z-index:3000;
  animation:fall linear forwards;
}

.confetti-piece:nth-child(odd){
  background:#fde96c;
}

.confetti-piece:nth-child(3n){
  background:#ffffff;
}

@keyframes fall{

  to{
    transform:
      translateY(110vh)
      rotate(720deg);

    opacity:0;
  }

}

`;

document.head.appendChild(style);