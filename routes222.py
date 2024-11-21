# {% extends "layout/base.html" %}

# {% block css %}
# <link rel="stylesheet" href="{{ url_for('static', filename='css/variable.css') }}">
# <link rel="stylesheet" href="{{ url_for('static', filename='css/style.css') }}">
# <link rel="stylesheet" href="{{ url_for('static', filename='css/output.css') }}">
# <link href="https://fonts.googleapis.com/icon?family=Material+Icons" rel="stylesheet">

# <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
# {% endblock css %}

# {% block content %}

#     <header>
#         {% include "includes/navbar.html" %}
#     </header>


#     <div class="flex flex-1">
#         {% include "includes/sidebar.html" %}



#         <main class="flex-1 p-5 mx-5 mt-24 ml-2 md:ml-60">

#             <div class="container">
#                 <div class="flex flex-col md:flex-row justify-between items-center mb-2">
#                     <div class="faculty-results-heading">
#                         <h2 class="text-lg p-2 font-bold primary">Printing Overall Results</h2>
#                     </div>
#                     <button class="print-button border border-gray-300 rounded-md px-4 py-2 text-sm text-white bg-[#004526]
#                     shadow-lg transition-all duration-300 transform hover:bg-[#023047] hover:text-white hover:shadow-2xl focus:outline-none"
#                     onclick="printOverallResults()">
#                         Download as Pdf
#                     </button>
#                 </div>

#                 <!--University Info -->
#                 <section id="universityinfo" class="p-3 mb-5">
#                     <div class="flex flex-col space-y-4 text-center mb-10 text-lg">
#                         <div class="flex justify-center items-center space-x-2">
#                             <span class="font-bold">Overall Results of Faculty Teaching Performance</span>
#                         </div>
#                         <div class="flex justify-center items-center space-x-2">
#                             <span class="font-bold">Central Mindanao University</span>
#                         </div>
#                         <div class="flex justify-center items-center space-x-2">
#                             <span class="font-bold">{{ selected_ay_name }}</span>
#                         </div>
                        
                        
#                     </div>

#                 </section>
#                 <!--Sentiment Overview -->
#                 <section>
#                         <div class="p-2 text-lg font-bold maze">
#                             <h2 class="primary">Sentiment Overview</h2>
#                         </div>
#                     <div class="grid grid-cols-1 md:grid-cols-4 gap-6">
                        
#                         <div class="bg-[#004526] text-white rounded-lg shadow-md mb-5 p-8 flex flex-col hvr-grow">
#                             <h2 class="text-lg font-semibold">Total Comments</h2>
#                             <h4 class="text-3xl font-bold text-center">{{ total_comments }} <span class="ml-2 text-sm">Comments</span></h4>
#                         </div>
#                         <div class="bg-white border-l-4 border-green-500 rounded-lg shadow-md mb-5 p-8 flex flex-col hvr-grow">
#                             <h2 class="text-lg font-semibold positive">Positive</h2>
#                             <h4 class="text-3xl font-bold text-center positive">{{ positive_count }} <span class="ml-2 text-sm primary">Comments</span></h4>
#                         </div>
#                         <div class="bg-white border-l-4 border-red-500 rounded-lg shadow-md mb-5 p-8 flex flex-col relative hvr-grow">
#                             <h2 class="text-lg font-semibold negative">Negative</h2>
#                             <h4 class="text-3xl font-bold text-center text-red-500">{{ negative_count }} <span class="ml-2 text-sm primary">Comments</span></h4>
#                         </div>
#                         <div class="bg-white border-l-4 border-yellow-500 rounded-lg shadow-md mb-5 p-8 flex flex-col relative hvr-grow">
#                             <h2 class="text-lg font-semibold neutral">Neutral</h2>
#                             <h4 class="text-3xl font-bold text-center neutral">{{ neutral_count }} <span class="ml-2 text-sm primary">Comments</span></h4>
#                         </div>
#                     </div>
#                 </section>

#                 <!--Progress Chart  -->
#                 <section>
#                     <div class="bg-white rounded-lg shadow-md mb-5 p-8 flex flex-col md:flex-row mt-6 border-2">
#                         <div class="flex-grow">
#                             <h2 class="text-lg font-semibold mb-4">Sentiment Analysis this semester</h2>                  
#                             <!-- Positive Sentiment -->
#                             <div class="flex items-center justify-between mb-2  primary">
#                                 <div class="flex items-center">
#                                     <span class="material-icons primary">thumb_up</span>
#                                     <span class="ml-2 primary">Positive</span>
#                                 </div>
#                                 <p class="text-3xl font-bold">{{ (positive_count / total_comments * 100) | round(2) if total_comments > 0 else 0 }}%</p>
#                             </div>
#                             <div class="w-full bg-gray-200 rounded-full mt-2">
#                                 <div class="bg-[#32de84] h-2 rounded-full" 
#                                 style="width: {{ (positive_count / total_comments * 100) | round(2) if total_comments > 0 else 0 }}%;">
#                                 </div>
#                             </div>
#                             <!-- Neutral Sentiment -->
#                             <div class="flex items-center justify-between mb-2 mt-4 primary">
#                                 <div class="flex items-center">
#                                     <span class="material-icons">more_horiz</span>
#                                     <span class="ml-2">Neutral</span>
#                                 </div>
#                                 <p class=" text-3xl font-bold">{{ (neutral_count / total_comments * 100) | round(2) if total_comments > 0 else 0 }}%</p>
#                             </div>
#                             <div class="w-full bg-gray-200 rounded-full mt-2">
#                                 <div class="bg-[#FFEB3B] h-2 rounded-full" 
#                                 style="width: {{ (neutral_count / total_comments * 100) | round(2) if total_comments > 0 else 0 }}%;"></div>
#                             </div>
#                             <!-- Negative Sentiment -->
#                             <div class="flex items-center justify-between mb-2 mt-4 primary">
#                                 <div class="flex items-center">
#                                     <span class="material-icons ">thumb_down</span>
#                                     <span class="ml-2">Negative</span>
#                                 </div>
#                                 <p class="text-3xl font-bold">{{ (negative_count / total_comments * 100) | round(2) if total_comments > 0 else 0 }}%</p>
#                             </div>
#                             <div class="w-full bg-gray-200 rounded-full mt-2">
#                                 <div class="bg-[#EF5350] h-2 rounded-full" 
#                                 style="width: {{ (negative_count / total_comments * 100) | round(2) if total_comments > 0 else 0 }}%;"></div>
#                             </div>
            
#                         </div>
#                         <!--Pie Chart -->
#                             <div class="mt-4 md:mt-0 md:ml-6">
#                                 <canvas id="sentimentPieChart" width="150" height="250"></canvas>
#                             </div>
                    
#                     </div>
#                     <div class="mt-4 mb-5">
#                         <h2 class="text-lg font-bold primary mb-2">Faculty Evaluation Sentiment Comparison </h2>
#                         <div class="overflow-x-auto">
#                             <div class="table-border">
#                                 <table class="data-table w-full border-collapse text-sm">
#                                     <thead class="table-header bg-gray-100">
#                                         <tr>
#                                             <th class="table-cell px-2 py-1 border border-gray-300">Semester</th>
#                                             <th class="table-cell px-2 py-1 border border-gray-300">Total Comments</th>
#                                             <th class="table-cell px-2 py-1 border border-gray-300">Positive</th>
#                                             <th class="table-cell px-2 py-1 border border-gray-300">Neutral</th>
#                                             <th class="table-cell px-2 py-1 border border-gray-300">Negative</th>
#                                         </tr>
#                                     </thead>
#                                     <tbody>
#                                         {% for semester in semester_sentiment_counts %}
#                                         <tr class="odd:bg-white even:bg-gray-50">
#                                             <td class="table-cell px-2 py-1 border border-gray-300">{{ semester.semester }}</td>
#                                             <td class="table-cell px-2 py-1 border border-gray-300">{{ semester.positive + semester.neutral + semester.negative }}</td>
#                                             <td class="table-cell px-2 py-1 border border-gray-300">{{ semester.positive }}</td>
#                                             <td class="table-cell px-2 py-1 border border-gray-300">{{ semester.neutral }}</td>
#                                             <td class="table-cell px-2 py-1 border border-gray-300">{{ semester.negative }}</td>
#                                         </tr>
#                                         {% endfor %}
#                                     </tbody>
#                                 </table>
                                
#                             </div>

#                         </div>
#                     </div>
#                     <section id="stockbar" class="mt-5 mb-2">
#                         <div class="bg-white rounded-lg shadow-md mt-5 border-2">
#                             <h2 class="text-lg font-semibold mb-4 p-4">Overall Semester Comparison</h2>
#                             <div class="flex justify-center items-center mb-5">
#                                 <canvas id="stackbarchart" width="600px" height="300px"></canvas>
#                             </div>
#                         </div>
#                     </section>
                                        
#                     <script>
#                         // Fetch the dynamic sentiment data passed from Flask
#                         const semesterData = {{ semester_sentiment_counts|tojson }};
                        
#                         // Labels for the X-axis (semester names)
#                         const labels = semesterData.map(item => item.semester);

#                         // Data for the stacked bar chart (for all semesters)
#                         const data = {
#                             labels: labels,
#                             datasets: [
#                                 {
#                                     label: 'Positive',
#                                     data: semesterData.map(item => item.positive),
#                                     backgroundColor: 'rgba(75, 192, 192, 0.5)', // Green color
#                                 },
#                                 {
#                                     label: 'Neutral',
#                                     data: semesterData.map(item => item.neutral),
#                                     backgroundColor: 'rgba(255, 159, 64, 0.5)', // Yellow color
#                                 },
#                                 {
#                                     label: 'Negative',
#                                     data: semesterData.map(item => item.negative),
#                                     backgroundColor: 'rgba(255, 99, 132, 0.5)', // Red color
#                                 },
#                             ]
#                         };

#                         // Configuration for the stacked bar chart
#                         const config = {
#                             type: 'bar',
#                             data: data,
#                             options: {
#                                 plugins: {
#                                     title: {
#                                         display: true,
#                                         text: 'Sentiment Analysis for All Semesters', // Title for the chart
#                                     },
#                                 },
#                                 responsive: true,
#                                 scales: {
#                                     x: {
#                                         stacked: true, // Stack bars on the x-axis
#                                     },
#                                     y: {
#                                         stacked: true, // Stack bars on the y-axis
#                                     },
#                                 },
#                             },
#                         };

#                         // Create and render the stacked bar chart
#                         const ctx = document.getElementById('stackbarchart').getContext('2d');
#                         new Chart(ctx, config);
#                     </script>
                
                    
#                 </section>

#                 <!--Print Layout Hidden -->
#                 <section id="printLayout" style="display: none;" >
#                     <div class="header border-b-2 mb-2">
#                         <div class="header-content text-center p-4">
#                             <h1>ANALYZING AND VISUALIZING COMMENTS IN CMU FACULTY EVALUATION SYSTEM</h1>
#                             <p class="primary">Empowering insights for continuous improvement</p>
#                         </div>
#                         <section id="university" class="p-3 mb-5">
#                             <div class="flex flex-col space-y-4 text-center mb-10 text-lg">
#                                 <div class="flex justify-center items-center space-x-2">
#                                     <span class="font-bold">Overall Results of Faculty Teaching Performance</span>
#                                 </div>
#                                 <div class="flex justify-center items-center space-x-2">
#                                     <span class="font-bold">Central Mindanao University</span>
#                                 </div>
#                                 <div class="flex justify-center items-center space-x-2">
#                                     <span class="font-bold">{{ default_semester.ay_name }}</span>
#                                 </div>
#                             </div>
#                         </section>
                        
#                         <section> 
#                             <div class="p-2 text-lg font-bold maze">
#                                 <h2 class="primary">Sentiment Overview</h2>
#                             </div>
#                             <div class="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-4 gap-6">
#                                 <div class="bg-[#004526] text-white rounded-lg shadow-md mb-5 p-8 flex flex-col hvr-grow">
#                                     <h2 class="text-lg font-semibold">Total Comments</h2>
#                                     <h4 class="text-3xl font-bold text-center">{{ total_comments }} <span class="ml-2 text-sm">Comments</span></h4>
#                                 </div>
#                                 <div class="bg-white border-l-4 border-green-500 rounded-lg shadow-md mb-5 p-8 flex flex-col hvr-grow">
#                                     <h2 class="text-lg font-semibold positive">Positive</h2>
#                                     <h4 class="text-3xl font-bold text-center positive">{{ positive_count }} <span class="ml-2 text-sm primary">Comments</span></h4>
#                                 </div>
#                                 <div class="bg-white border-l-4 border-red-500 rounded-lg shadow-md mb-5 p-8 flex flex-col relative hvr-grow">
#                                     <h2 class="text-lg font-semibold negative">Negative</h2>
#                                     <h4 class="text-3xl font-bold text-center text-red-500">{{ negative_count }} <span class="ml-2 text-sm primary">Comments</span></h4>
#                                 </div>
#                                 <div class="bg-white border-l-4 border-yellow-500 rounded-lg shadow-md mb-5 p-8 flex flex-col relative hvr-grow">
#                                     <h2 class="text-lg font-semibold neutral">Neutral</h2>
#                                     <h4 class="text-3xl font-bold text-center neutral">{{ neutral_count }} <span class="ml-2 text-sm primary">Comments</span></h4>
#                                 </div>
#                             </div>
#                         </section>
                
#                         <section>
#                             <div class="bg-white rounded-lg shadow-md mb-5 p-2 flex flex-col md:flex-row mt-6 border-2">
#                                 <div class="flex-grow">
#                                     <h2 class="text-lg font-semibold mb-4">Sentiment Analysis this semester</h2>
                            
#                                     <!-- Positive Sentiment -->
#                                     <div class="flex items-center justify-between mb-2 primary">
#                                         <div class="flex items-center">
#                                             <span class="material-icons primary">thumb_up</span>
#                                             <span class="ml-2 primary">Positive</span>
#                                         </div>
#                                         <p class="text-3xl font-bold">{{ (positive_count / total_comments * 100) | round(2) if total_comments > 0 else 0 }}%</p>
#                                     </div>
#                                     <div class="progress-bar bg-gray-200 rounded-full mt-2">
#                                         <div class="progress-fill positive-fill" style="width: {{ (positive_count / total_comments * 100) | round(2) if total_comments > 0 else 0 }}%;"></div>
#                                     </div>
                            
#                                     <!-- Neutral Sentiment -->
#                                     <div class="flex items-center justify-between mb-2 mt-4 primary">
#                                         <div class="flex items-center">
#                                             <span class="material-icons">more_horiz</span>
#                                             <span class="ml-2">Neutral</span>
#                                         </div>
#                                         <p class="text-3xl font-bold">{{ (neutral_count / total_comments * 100) | round(2) if total_comments > 0 else 0 }}%</p>
#                                     </div>
#                                     <div class="progress-bar bg-gray-200 rounded-full mt-2">
#                                         <div class="progress-fill neutral-fill" style="width: {{ (neutral_count / total_comments * 100) | round(2) if total_comments > 0 else 0 }}%;"></div>
#                                     </div>
                            
#                                     <!-- Negative Sentiment -->
#                                     <div class="flex items-center justify-between mb-2 mt-4 primary">
#                                         <div class="flex items-center">
#                                             <span class="material-icons">thumb_down</span>
#                                             <span class="ml-2">Negative</span>
#                                         </div>
#                                         <p class="text-3xl font-bold">{{ (negative_count / total_comments * 100) | round(2) if total_comments > 0 else 0 }}%</p>
#                                     </div>
#                                     <div class="progress-bar bg-gray-200 rounded-full mt-2">
#                                         <div class="progress-fill negative-fill" style="width: {{ (negative_count / total_comments * 100) | round(2) if total_comments > 0 else 0 }}%;"></div>
#                                     </div>
#                                 </div>
#                             </div>
#                         </section>                        
#                     </div>
#                     <div class="mt-4 mb-5">
#                         <h2 class="text-lg font-bold primary mb-2">Faculty Evaluation Sentiment Comparison </h2>
#                         <div class="overflow-x-auto">
#                             <div class="table-border">
#                                 <table class="data-table w-full border-collapse text-sm">
#                                     <thead class="table-header bg-gray-100">
#                                         <tr>
#                                             <th class="table-cell px-2 py-1 border border-gray-300">Semester</th>
#                                             <th class="table-cell px-2 py-1 border border-gray-300">Total Comments</th>
#                                             <th class="table-cell px-2 py-1 border border-gray-300">Positive</th>
#                                             <th class="table-cell px-2 py-1 border border-gray-300">Neutral</th>
#                                             <th class="table-cell px-2 py-1 border border-gray-300">Negative</th>
#                                         </tr>
#                                     </thead>
#                                     <tbody>
#                                         {% for semester in semester_sentiment_counts %}
#                                         <tr class="odd:bg-white even:bg-gray-50">
#                                             <td class="table-cell px-2 py-1 border border-gray-300">{{ semester.semester }}</td>
#                                             <td class="table-cell px-2 py-1 border border-gray-300">{{ semester.positive + semester.neutral + semester.negative }}</td>
#                                             <td class="table-cell px-2 py-1 border border-gray-300">{{ semester.positive }}</td>
#                                             <td class="table-cell px-2 py-1 border border-gray-300">{{ semester.neutral }}</td>
#                                             <td class="table-cell px-2 py-1 border border-gray-300">{{ semester.negative }}</td>
#                                         </tr>
                                        
#                                         {% endfor %}
#                                     </tbody>
#                                 </table>
#                             </div>
#                         </div>
#                     </div>
                    

#                 </section>

#             </div>
#         </main>
#     </div>

# <!--Script -->


#     <!--// Pie Chart for Sentiment Analysis -->

#     <script>
#         document.addEventListener("DOMContentLoaded", function () {      
#             const ctxPie = document.getElementById('sentimentPieChart').getContext('2d');
#             new Chart(ctxPie, {
#                 type: 'pie',
#                 data: {
#                     labels: ['Positive', 'Neutral', 'Negative'],
#                     datasets: [{
#                         label: 'Sentiments',
#                         data: [
#                             {{ positive_count }},
#                             {{ neutral_count }},
#                             {{ negative_count }}
#                         ],
#                         backgroundColor: ['#32de84', '#FFEB3B', '#EF5350']
#                     }]
#                 },
#                 options: {
#                     responsive: false,
#                     plugins: {
#                         legend: { position: 'top' }
#                     }
#                 }
#             }); 
#         });
#     </script>
            
#     <script>
#         function printOverallResults() {
#             const printContent = document.getElementById('printLayout').innerHTML;
#             const originalContent = document.body.innerHTML;
        
#             try {
#                 document.body.innerHTML = printContent;
#                 window.print();
#             } finally {
#                 document.body.innerHTML = originalContent;
#                 if (typeof history !== 'undefined' && history.pushState) {
#                     history.go(0); 
#                 }
#             }
#         }
#     </script>







# {% endblock %}