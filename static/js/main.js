
// Readmore function in Home // 
function toggleText() {
    const moreText = document.getElementById("moreText");
    const seeMore = document.getElementById("seeMore");

    if (moreText && seeMore) {
        const isVisible = moreText.style.display !== "none";
        moreText.style.display = isVisible ? "none" : "inline";
        seeMore.textContent = isVisible ? "See more" : "See less";
    }
}

// end-Readmore function in Home // 


// Toggle mobile menu visibility
            document.addEventListener('DOMContentLoaded', () => {
                const mobileMenuButton = document.getElementById('mobile-menu-button');
                const mobileMenu = document.getElementById('mobile-menu');

                if (mobileMenuButton && mobileMenu) {
                    mobileMenuButton.addEventListener('click', () => {
                        mobileMenu.classList.toggle('hidden');
                    });
                }
            });

            function closeMobileMenu() {
                const mobileMenu = document.getElementById('mobile-menu');
                if (mobileMenu) {
                    mobileMenu.classList.add('hidden');
                }
            }

            function showSection(section) {
                const homeSection = document.getElementById('home-section');
                const aboutSection = document.getElementById('about-section');
                const contactSection = document.getElementById('contact-section');

                if (homeSection && aboutSection && contactSection) {
                    homeSection.classList.add('hidden');
                    aboutSection.classList.add('hidden');
                    contactSection.classList.add('hidden');

                    if (section === 'home') {
                        homeSection.classList.remove('hidden');
                    } else if (section === 'about') {
                        aboutSection.classList.remove('hidden');
                    } else if (section === 'contact') {
                        contactSection.classList.remove('hidden');
                    }
                }

                // Toggle active class on links
                const link = document.getElementById(`${section}-link`);
                if (link) {
                    document.getElementById('home-link').classList.remove('active');
                    document.getElementById('about-link').classList.remove('active');
                    document.getElementById('contact-link').classList.remove('active');
                    link.classList.add('active');
                }

                closeMobileMenu();
            }


// end- Toggle mobile menu visibility



function updateDepartments() {
    const collegeDropdown = document.getElementById('filterCollege');
    const departmentDropdown = document.getElementById('filterDepartment');
    const selectedCollege = collegeDropdown.value;

    // Save the currently selected department
    const selectedDepartment = departmentDropdown.value;

    // Loop through department options and toggle visibility
    Array.from(departmentDropdown.options).forEach((option) => {
        const departmentCollegeId = option.getAttribute('data-college-id');
        if (departmentCollegeId === selectedCollege || !departmentCollegeId) {
            option.style.display = '';
        } else {
            option.style.display = 'none';
        }
    });

    // Restore the selected department if valid
    if (selectedDepartment) {
        const validOption = Array.from(departmentDropdown.options).find(
            (option) => option.value === selectedDepartment && option.style.display !== 'none'
        );

        if (validOption) {
            departmentDropdown.value = selectedDepartment;
        } else {
            departmentDropdown.value = '';
        }
    } else {
        departmentDropdown.value = '';
    }
}


document.addEventListener('DOMContentLoaded', () => {
    const toggleButton = document.getElementById('toggle-button');
    const sidebar = document.getElementById('sidebar');

    // Check localStorage for previous collapse state and apply it
    if (localStorage.getItem('sidebarCollapsed') === 'true') {
        sidebar.classList.add('collapsed');
    }

    toggleButton.addEventListener('click', function () {
        sidebar.classList.toggle('collapsed');
        
        // Update localStorage with the new state
        const isCollapsed = sidebar.classList.contains('collapsed');
        localStorage.setItem('sidebarCollapsed', isCollapsed);
    });
});


document.addEventListener('DOMContentLoaded', () => {
    const notificationToggle = document.getElementById('notification-toggle');
    const profileMenuToggle = document.getElementById('profile-menu-toggle');

    if (notificationToggle) {
        notificationToggle.addEventListener('change', function () {
            document.body.style.overflow = this.checked ? 'hidden' : 'auto';
        });
    }

    if (profileMenuToggle) {
        profileMenuToggle.addEventListener('change', function () {
            document.body.style.overflow = this.checked ? 'hidden' : 'auto';
        });
    }
});

// Mobile View for sidebar display 

document.getElementById('mobile-menu-button').addEventListener('click', function() {
    const menu = document.getElementById('mobile-menu');
    menu.classList.toggle('show');
});


//mobile exit in headers
function toggleMobileMenu() {
    const mobileMenu = document.getElementById('mobile-menu');
    mobileMenu.classList.toggle('hidden');
  }

  //searching

  function filterTable() {
    const searchInput = document.getElementById('searchUsers').value.toLowerCase();
    const filterCollege = document.getElementById('filterCollege').value.toLowerCase();
    const tableBody = document.getElementById('accountsTableBody');
    const rows = tableBody.getElementsByTagName('tr');

    for (let i = 0; i < rows.length; i++) {
        const nameCell = rows[i].getElementsByTagName('td')[0]; 
        const collegeCell = rows[i].getElementsByTagName('td')[1]; 
        let nameText = nameCell.textContent || nameCell.innerText;
        let collegeText = collegeCell.textContent || collegeCell.innerText;

        // Check for search input
        const nameMatch = nameText.toLowerCase().includes(searchInput);
        const collegeMatch = filterCollege === "" || collegeText.toLowerCase() === filterCollege;

        if (nameMatch && collegeMatch) {
            rows[i].style.display = "";
        } else {
            rows[i].style.display = "none";
        }
    }
}



// felter User name 

function filterTable() {
    const input = document.getElementById('searchUsers');
    const filter = input.value.toLowerCase();
    const tableBody = document.getElementById('accountsTableBody');
    const rows = tableBody.getElementsByTagName('tr');

    for (let i = 0; i < rows.length; i++) {
        const nameCell = rows[i].getElementsByTagName('td')[0];
        const emailCell = rows[i].getElementsByTagName('td')[1];

        if (nameCell || emailCell) {
            const nameText = nameCell.textContent || nameCell.innerText;
            const emailText = emailCell.textContent || emailCell.innerText;

            if (nameText.toLowerCase().indexOf(filter) > -1 || emailText.toLowerCase().indexOf(filter) > -1) {
                rows[i].style.display = '';
            } else {
                rows[i].style.display = 'none';
            }
        }
    }
}   

// Felter college in faculty //

function applyFilters() {
    const searchQuery = document.getElementById('searchUsers').value;
    const selectedCollege = document.getElementById('filterCollege').value;
    const url = new URL(window.location.href);
    
    // Update the search and college parameters in the URL
    if (searchQuery) {
        url.searchParams.set('search', searchQuery);
    } else {
        url.searchParams.delete('search');
    }

    if (selectedCollege) {
        url.searchParams.set('college', selectedCollege);
    } else {
        url.searchParams.delete('college');
    }

    window.location.href = url.toString();
}

//bar chart 

