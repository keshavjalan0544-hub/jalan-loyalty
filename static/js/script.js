/**
 * JALAN SALES — MP BIRLA CHETAK CEMENT
 * FINAL PREMIUM JS
 * Industrial Premium UI Interactions
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
        .slice(0, 10);

    });

  });

  /* ─────────────────────────────────────────────
     LOGIN FORM VALIDATION
  ───────────────────────────────────────────── */

  const loginForm = document.getElementById('loginForm');

  if (loginForm) {

    loginForm.addEventListener('submit', (e) => {

      const name = document.getElementById('name');
      const phone = document.getElementById('phone');

      if (!name || !phone) return;

      const nameValue = name.value.trim();
      const phoneValue = phone.value.trim();

      removeErrors();

      if (!nameValue || !phoneValue) {

        e.preventDefault();

        shake(loginForm);

        if (!nameValue) {
          showError(name, 'Please enter your name');
        }

        if (!phoneValue) {
          showError(phone, 'Please enter mobile number');
        }

        return;
      }

      if (!/^\d{10}$/.test(phoneValue)) {

        e.preventDefault();

        shake(loginForm);

        showError(phone, 'Enter valid 10 digit number');

        return;
      }

      const btn = loginForm.querySelector('button[type="submit"]');

      if (btn) {

        btn.disabled = true;

        btn.innerHTML = `
          <span class="spinner"></span>
          Please Wait...
        `;

      }

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
     PROGRESS BAR
  ───────────────────────────────────────────── */

  const progressFill = document.getElementById('progressFill');

  if (progressFill) {

    const target = parseInt(
      progressFill.dataset.target || 0
    );

    setTimeout(() => {

      progressFill.style.width = target + '%';

    }, 400);

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
     RESET CONFIRM
  ───────────────────────────────────────────── */

  document.querySelectorAll('.confirm-reset')
    .forEach(btn => {

      btn.addEventListener('click', (e) => {

        const confirmReset = confirm(
          'Reset all visits and rewards?'
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

      try {

        await navigator.clipboard.writeText(
          copyQrBtn.dataset.url
        );

        copyQrBtn.innerHTML = '✅ Copied';

        setTimeout(() => {

          copyQrBtn.innerHTML =
            '📋 Copy Scan URL';

        }, 2000);

      } catch {

        alert('Copy failed');

      }

    });

  }

  /* ─────────────────────────────────────────────
     HOVER EFFECTS
  ───────────────────────────────────────────── */

  const cards = document.querySelectorAll('.glass-card');

  cards.forEach(card => {

    card.addEventListener('mousemove', (e) => {

      if (window.innerWidth < 768) return;

      const rect = card.getBoundingClientRect();

      const x = e.clientX - rect.left;
      const y = e.clientY - rect.top;

      const rotateY =
        ((x / rect.width) - 0.5) * 8;

      const rotateX =
        ((y / rect.height) - 0.5) * -8;

      card.style.transform =
        `perspective(1000px)
         rotateX(${rotateX}deg)
         rotateY(${rotateY}deg)
         translateY(-2px)`;

    });

    card.addEventListener('mouseleave', () => {

      card.style.transform =
        'perspective(1000px) rotateX(0) rotateY(0)';

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

function showError(field, message) {

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
   CLOSE POPUP
───────────────────────────────────────────── */

function closeRewardPopup() {

  const popup = document.getElementById('rewardPopup');

  if (!popup) return;

  popup.style.opacity = '0';

  setTimeout(() => {

    popup.remove();

  }, 300);

}

/* ─────────────────────────────────────────────
   CONFETTI
───────────────────────────────────────────── */

function launchConfetti() {

  for (let i = 0; i < 40; i++) {

    const confetti = document.createElement('div');

    confetti.className = 'confetti-piece';

    confetti.style.left =
      Math.random() * 100 + 'vw';

    confetti.style.animationDuration =
      (Math.random() * 3 + 2) + 's';

    confetti.style.opacity =
      Math.random();

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