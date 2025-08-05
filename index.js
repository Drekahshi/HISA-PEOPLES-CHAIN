const hamburger = document.getElementById('hamburger');
const navMenu = document.getElementById('navMenu');
hamburger.addEventListener('click', () => {
    navMenu.classList.toggle('open');
    hamburger.setAttribute('aria-expanded', navMenu.classList.contains('open'));
});

// Dropdowns for all menu items
document.querySelectorAll('.nav-link').forEach(link => {
    const dropdown = link.querySelector('.dropdown-menu');
    if (dropdown) {
        link.addEventListener('click', function(e) {
            if(window.innerWidth <= 900) {
                e.stopPropagation();
                // Close other open dropdowns
                document.querySelectorAll('.dropdown-menu').forEach(otherDropdown => {
                    if (otherDropdown !== dropdown) {
                        otherDropdown.classList.remove('show');
                    }
                });
                dropdown.classList.toggle('show');
            }
        });
    }
});

document.addEventListener('click', function() {
    document.querySelectorAll('.dropdown-menu').forEach(dropdown => {
        dropdown.classList.remove('show');
    });
});

// Modal functionality
const exploreEcosystemBtn = document.getElementById('exploreEcosystemBtn');
const viewWhitepapersBtn = document.getElementById('viewWhitepapersBtn');
const ecosystemModal = document.getElementById('ecosystemModal');
const whitepapersModal = document.getElementById('whitepapersModal');
const closeEcosystemModal = document.getElementById('closeEcosystemModal');
const closeWhitepapersModal = document.getElementById('closeWhitepapersModal');

// Open Ecosystem Modal
exploreEcosystemBtn.addEventListener('click', () => {
    ecosystemModal.style.display = 'block';
    document.body.style.overflow = 'hidden'; // Prevent background scrolling
});

// Open Whitepapers Modal
viewWhitepapersBtn.addEventListener('click', () => {
    whitepapersModal.style.display = 'block';
    document.body.style.overflow = 'hidden'; // Prevent background scrolling
});

// Close Ecosystem Modal
closeEcosystemModal.addEventListener('click', () => {
    ecosystemModal.style.display = 'none';
    document.body.style.overflow = 'auto'; // Restore scrolling
});

// Close Whitepapers Modal
closeWhitepapersModal.addEventListener('click', () => {
    whitepapersModal.style.display = 'none';
    document.body.style.overflow = 'auto'; // Restore scrolling
});

// Close modals when clicking outside
window.addEventListener('click', (event) => {
    if (event.target === ecosystemModal) {
        ecosystemModal.style.display = 'none';
        document.body.style.overflow = 'auto';
    }
    if (event.target === whitepapersModal) {
        whitepapersModal.style.display = 'none';
        document.body.style.overflow = 'auto';
    }
});

// Close modals with Escape key
document.addEventListener('keydown', (event) => {
    if (event.key === 'Escape') {
        ecosystemModal.style.display = 'none';
        whitepapersModal.style.display = 'none';
        document.body.style.overflow = 'auto';
    }
});