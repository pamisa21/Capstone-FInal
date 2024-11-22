    document.addEventListener("DOMContentLoaded", function () {
        const dashboardDropdown = document.getElementById("dashboardSemesterDropdown");
        const collegeDropdown = document.getElementById("filterCollege");
        const departmentDropdown = document.getElementById("filterDepartment");
        const printButton = document.getElementById("printButton");
        const signOutLink = document.getElementById("signOutLink");

        // Get the selected values from localStorage or query parameters
        let selectedSemester = localStorage.getItem("selectedSemester") || new URLSearchParams(window.location.search).get('ay_id');
        let selectedCollege = localStorage.getItem("selectedCollege");
        let selectedDepartment = localStorage.getItem("selectedDepartment");

        // Set default values for the dropdowns if they exist in localStorage or URL
        if (selectedSemester) {
            dashboardDropdown.value = selectedSemester;
        }
        if (selectedCollege) {
            collegeDropdown.value = selectedCollege;
            updatePrintButtonText();
        }
        if (selectedDepartment) {
            departmentDropdown.value = selectedDepartment;
        }

        // Store selected values in localStorage when changed
        dashboardDropdown.addEventListener("change", function () {
            localStorage.setItem("selectedSemester", dashboardDropdown.value);
            window.location.href = `/dashboard?ay_id=${dashboardDropdown.value}&college_id=${collegeDropdown.value}&department_id=${departmentDropdown.value}`;
        });

        collegeDropdown.addEventListener("change", function () {
            localStorage.setItem("selectedCollege", collegeDropdown.value);
            window.location.href = `/dashboard?ay_id=${dashboardDropdown.value}&college_id=${collegeDropdown.value}&department_id=${departmentDropdown.value}`;
            updatePrintButtonText();
        });

        departmentDropdown.addEventListener("change", function () {
            localStorage.setItem("selectedDepartment", departmentDropdown.value);
            window.location.href = `/dashboard?ay_id=${dashboardDropdown.value}&college_id=${collegeDropdown.value}&department_id=${departmentDropdown.value}`;
        });

        // Clear localStorage when Sign Out is clicked
        signOutLink.addEventListener("click", function () {
            
            localStorage.removeItem("selectedCollege");
            localStorage.removeItem("selectedDepartment");
        });

        // Update the print button text
        function updatePrintButtonText() {
            const selectedCollegeId = collegeDropdown.value;
            const selectedDepartmentId = departmentDropdown.value;
            const selectedSemesterId = dashboardDropdown.value;

            const selectedCollegeName = collegeDropdown.options[collegeDropdown.selectedIndex]?.text || "Select College";
            const selectedDepartmentName = departmentDropdown.options[departmentDropdown.selectedIndex]?.text || "Select Department";

            let buttonText = "Print Overall Results";
            let route = "/print_dashboard";

            if (selectedCollegeId) {
                buttonText = `Print ${selectedCollegeName} Results`;
                route = `/print_colleges?college_id=${selectedCollegeId}&ay_id=${selectedSemesterId}`;
            }
            if (selectedDepartmentId) {
                buttonText = `Print ${selectedDepartmentName} Results`;
                route = `/print_department?department_id=${selectedDepartmentId}&ay_id=${selectedSemesterId}`;
            }

            if (selectedCollegeId && selectedDepartmentId) {
                buttonText = `Print ${selectedCollegeName} - ${selectedDepartmentName} Results`.slice(0, 50);
                route = `/print_department?college_id=${selectedCollegeId}&department_id=${selectedDepartmentId}&ay_id=${selectedSemesterId}`;
            }

            if (!selectedSemesterId) {
                route += `&ay_id=${getLatestSemesterId()}`;
            }

            printButton.innerHTML = `<a href="${route}">${buttonText}</a>`;
        }
    });

    function updateDashboard() {
        const selectedCollegeId = document.getElementById("filterCollege").value;
        const selectedSemester = document.getElementById("dashboardSemesterDropdown").value;
        const selectedDepartmentId = document.getElementById("filterDepartment").value;

        window.location.href = `/dashboard?college_id=${selectedCollegeId}&ay_id=${selectedSemester}&department_id=${selectedDepartmentId}`;
    }





    
document.addEventListener("DOMContentLoaded", function() {
const departmentDropdown = document.getElementById("filterDepartment");
const facultyList = document.getElementById("faculty-list");
const wordCloudSection = document.getElementById("wordCloudSection");
const stockbar = document.getElementById("stockbar");

// Initially, hide the faculty list
facultyList.classList.add('hidden');
wordCloudSection.classList.add('hidden');
stockbar.classList.add('hidden');

// Show or hide the faculty list when a department is selected
departmentDropdown.addEventListener("change", function() {
  if (departmentDropdown.value) {
      facultyList.classList.remove('hidden');
      wordCloudSection.classList.remove('hidden');
      stockbar.classList.remove('hidden'); // Show faculty list when a department is selected
  } else {
      facultyList.classList.add('hidden'); 
      wordCloudSection.classList.add('hidden');
      stockbar.classList.add('hidden'); // Hide faculty list when no department is selected
  }   
});

// Check the current department on page load (in case there is a saved value in localStorage)
if (departmentDropdown.value) {
  facultyList.classList.remove('hidden');
  wordCloudSection.classList.remove('hidden');
  stockbar.classList.remove('hidden');
}
});




