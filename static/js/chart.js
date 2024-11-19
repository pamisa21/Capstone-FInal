// selected semester

document.addEventListener("DOMContentLoaded", function() {
  const dashboardDropdown = document.getElementById("dashboardSemesterDropdown");
  const collegeDropdown = document.getElementById("filterCollege");
  const departmentDropdown = document.getElementById("filterDepartment");
  const printButton = document.getElementById("printButton");

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
  dashboardDropdown.addEventListener("change", function() {
      localStorage.setItem("selectedSemester", dashboardDropdown.value);
      window.location.href = `/dashboard?ay_id=${dashboardDropdown.value}&college_id=${collegeDropdown.value}&department_id=${departmentDropdown.value}`;
  });

  collegeDropdown.addEventListener("change", function() {
      localStorage.setItem("selectedCollege", collegeDropdown.value);
      window.location.href = `/dashboard?ay_id=${dashboardDropdown.value}&college_id=${collegeDropdown.value}&department_id=${departmentDropdown.value}`;
      updatePrintButtonText(); // Update the button text when college changes
  });

  departmentDropdown.addEventListener("change", function() {
      localStorage.setItem("selectedDepartment", departmentDropdown.value);
      window.location.href = `/dashboard?ay_id=${dashboardDropdown.value}&college_id=${collegeDropdown.value}&department_id=${departmentDropdown.value}`;
  });





  //Update text Print 
  function updatePrintButtonText() {
    const selectedCollegeId = collegeDropdown.value;
    const selectedDepartmentId = departmentDropdown.value;
    const selectedSemesterId = dashboardDropdown.value;

    const selectedCollegeName = collegeDropdown.options[collegeDropdown.selectedIndex]?.text || "Select College";
    const selectedDepartmentName = departmentDropdown.options[departmentDropdown.selectedIndex]?.text || "Select Department";

    let buttonText = "Print Overall Results"; // Default button text
    let route = "/print_dashboard"; // Default route

    if (selectedCollegeId) {
        buttonText = `Print ${selectedCollegeName} Results`;
        route = `/print_colleges?college_id=${selectedCollegeId}&ay_id=${selectedSemesterId}`;
    }
    if (selectedDepartmentId) {
        buttonText = `Print ${selectedDepartmentName} Results`;
        route = `/print_department?department_id=${selectedDepartmentId}&ay_id=${selectedSemesterId}`;
    }

    if (selectedCollegeId && selectedDepartmentId) {
        buttonText = `Prints ${selectedCollegeId} - ${selectedDepartmentName} Results`;
        buttonText = buttonText.slice(0, 50);  // Trims the text to 20 characters
        route = `/print_department?college_id=${selectedCollegeId}&department_id=${selectedDepartmentId}&ay_id=${selectedSemesterId}`;
    }
    
    // If no semester selected, ensure the latest semester is passed as a parameter
    if (!selectedSemesterId) {
        // Fetch the latest semester (can be done via AJAX or pre-passing the data)
        route += `&ay_id=${getLatestSemesterId()}`; // Add latest semester if none is selected
    }

    // Update the button's text and link
    printButton.innerHTML = `<a href="${route}">${buttonText}</a>`;
}

});
        

//Department 

document.addEventListener("DOMContentLoaded", function() {
  const departmentDropdown = document.getElementById("filterDepartment");
  const savedDepartment = localStorage.getItem("selectedDepartment");

  // Load last selected department if available
  if (savedDepartment) {
      departmentDropdown.value = savedDepartment;
  }

  // Save selected department to localStorage and refresh the page on change
  departmentDropdown.addEventListener("change", function() {
      localStorage.setItem("selectedDepartment", departmentDropdown.value);
      updateDashboard(); // Call the function to update the dashboard with the selected department
  });
});

function updateDashboard() {
  const selectedCollegeId = document.getElementById("filterCollege").value;
  const selectedSemester = document.getElementById("dashboardSemesterDropdown").value;
  const selectedDepartmentId = document.getElementById("filterDepartment").value;

  window.location.href = `/dashboard?college_id=${selectedCollegeId}&ay_id=${selectedSemester}&department_id=${selectedDepartmentId}`; // Reload with college_id, ay_id, and department_id
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




// window.onbeforeunload = function() {
//     localStorage.removeItem("selectedSemester");
//     localStorage.removeItem("selectedCollege");
//     localStorage.removeItem("selectedDepartment");
// };