let currentJobs = [];

async function fetchJobs() {
    const title = document.getElementById('jobTitle').value;
    const location = document.getElementById('location').value;
    const btnText = document.getElementById('btnText');
    const btnLoader = document.getElementById('btnLoader');
    const jobsContainer = document.getElementById('jobsContainer');

    if (!title || !location) {
        alert("Please enter both Job Title and Location.");
        return;
    }

    btnText.textContent = "Searching...";
    btnLoader.classList.remove('hidden');
    jobsContainer.innerHTML = '<div class="text-center py-10 text-gray-400">Scanning job boards...</div>';
    document.getElementById('resultsMeta').classList.add('hidden');
    document.getElementById('skillsContainer').classList.add('hidden');

    try {
        const response = await fetch(`http://localhost:5000/search?title=${encodeURIComponent(title)}&location=${encodeURIComponent(location)}`);
        const data = await response.json();
        currentJobs = data.jobs;

        renderJobs(currentJobs);
        renderSkills(data.skills_count);
        document.getElementById('resultsMeta').classList.remove('hidden');
    } catch (error) {
        console.error("Error fetching jobs:", error);
        jobsContainer.innerHTML = '<div class="text-center py-10 text-red-500">Failed to fetch jobs. Ensure the backend is running on port 5000.</div>';
    } finally {
        btnText.textContent = "Find Fresh Jobs";
        btnLoader.classList.add('hidden');
    }
}

function renderJobs(jobs) {
    const container = document.getElementById('jobsContainer');
    const countLabel = document.getElementById('resultCount');
    container.innerHTML = '';
    countLabel.textContent = `${jobs.length} fresh jobs found`;

    if (jobs.length === 0) {
        container.innerHTML = '<div class="text-center py-10 text-gray-500">No jobs found matching your criteria in the last 24 hours.</div>';
        return;
    }

    jobs.forEach((job, index) => {
        const card = document.createElement('div');
        card.className = "bg-white p-5 rounded-lg border border-gray-100 hover:shadow-md transition-shadow group";
        card.innerHTML = `
            <div class="flex justify-between items-start">
                <div>
                    <h3 class="font-bold text-lg text-gray-800 group-hover:text-blue-600 transition-colors">${job.title}</h3>
                    <p class="text-gray-600 text-sm font-medium">${job.company} • ${job.location}</p>
                    ${job.salary && job.salary !== "Not Listed" ? `<p class="text-green-600 text-sm font-semibold mt-1">💰 ${job.salary}</p>` : ''}
                </div>
                <span class="bg-green-100 text-green-700 text-xs font-bold px-2 py-1 rounded-full flex items-center gap-1">
                    <span class="w-2 h-2 bg-green-500 rounded-full animate-pulse"></span>
                    ${job.posted_date}
                </span>
            </div>
            <div class="mt-4 pt-3 border-t border-gray-50 flex justify-between items-center">
                <button onclick="viewDescription('${job.link}','desc-${index}')" class="text-sm font-medium text-gray-600 hover:text-gray-900 flex items-center gap-1">
                    <svg xmlns="http://www.w3.org/2000/svg" class="h-4 w-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13 16h-1v-4h-1m1-4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
                    </svg>
                    View Details
                </button>
                <a href="${job.link}" target="_blank" class="text-sm font-semibold text-blue-600 hover:text-blue-800">Quick Apply &rarr;</a>
            </div>
            <div id="desc-${index}" class="hidden mt-4 p-4 bg-gray-50 rounded text-sm text-gray-700 border border-gray-200">
                <div class="animate-pulse flex space-x-4">
                    <div class="flex-1 space-y-4 py-1">
                        <div class="h-4 bg-gray-200 rounded w-3/4"></div>
                        <div class="space-y-2">
                            <div class="h-4 bg-gray-200 rounded"></div>
                            <div class="h-4 bg-gray-200 rounded w-5/6"></div>
                        </div>
                    </div>
                </div>
            </div>
        `;
        container.appendChild(card);
    });
}

async function viewDescription(url, elementId) {
    const container = document.getElementById(elementId);

    if (!container.classList.contains('hidden') && container.dataset.loaded === "true") {
        container.classList.add('hidden');
        return;
    }

    container.classList.remove('hidden');

    if (container.dataset.loaded === "true") return;

    try {
        const response = await fetch(`http://localhost:5000/description?url=${encodeURIComponent(url)}`);
        const data = await response.json();
        if (data && data.description) {
            let content = data.description;
            if (data.salary && data.salary !== "Not Listed") {
                content = `<div class="mb-3 p-2 bg-green-50 border-l-4 border-green-500 rounded"><p class="text-green-700 font-semibold">💰 Salary: ${data.salary}</p></div>` + content;
            }
            container.innerHTML = content;
            container.dataset.loaded = "true";
        } else {
            container.innerHTML = '<p class="text-gray-500">Description not available.</p>';
        }
    } catch (error) {
        console.error("Error loading description:", error);
        container.innerHTML = '<p class="text-red-500">Failed to load description.</p>';
    }
}

function renderSkills(skills) {
    const container = document.getElementById('skillsContainer');
    const list = document.getElementById('skillsList');

    if (!skills || Object.keys(skills).length === 0) {
        container.classList.add('hidden');
        return;
    }

    list.innerHTML = '';
    container.classList.remove('hidden');

    const sortedSkills = Object.entries(skills).sort(([, a], [, b]) => b - a);

    sortedSkills.forEach(([skill, count]) => {
        const badge = document.createElement('span');
        badge.className = "bg-white text-blue-700 text-xs font-medium px-2.5 py-1 rounded border border-blue-200 shadow-sm";
        badge.textContent = `${skill} (${count})`;
        list.appendChild(badge);
    });
}
