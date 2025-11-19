const api = "https://optcg-asset-changer-web.onrender.com";

// Wake up the server
fetch(api + "/ping", {
    method: "GET",
});

// Load saved images from localStorage on page load
let savedImages = {};
try {
    const stored = localStorage.getItem('unityTextures');
    if (stored) {
        savedImages = JSON.parse(stored);
    }
} catch (e) {
    console.error('Error loading from localStorage:', e);
}

// Save images to localStorage
function saveToLocalStorage() {
    try {
        localStorage.setItem('unityTextures', JSON.stringify(savedImages));
    } catch (e) {
        console.error('Error saving to localStorage:', e);
        showStatus('Warning: Unable to save images. Storage may be full.', false);
    }
}

const textures = [
    { name: "buttonLong_beige", size: "190x49", desc: "the button for everything, it gets stretched" },
    { name: "HighlightSquare", size: "178x178", desc: "highlight on selected cards and don" },
    { name: "Arrow", size: "60x30", desc: "the red arrow showing who attacks and where" },
    { name: "AttackArrow", size: "200x100", desc: "the wide power is displayed over" },
    { name: "YouLose", size: "391x90", desc: "you lose screen" },
    { name: "YouWin", size: "377x88", desc: "you win screen" },
    { name: "toppng.com-download-blue-glow-effect-1024x1024", size: "835x835", desc: "the glow effect for prio - it has a blue filter over :3" },
    { name: "panel_beige", size: "100x100", desc: "background for choosing game and some labels" },
    { name: "arrow_beige", size: "100x100", desc: "arrows for checking trash" },
    { name: "Background", size: "32x32", desc: "chat background" },
    { name: "DropdownArrow", size: "64x64", desc: "arrow on all dropdowns" },
    { name: "Checkmark", size: "64x64", desc: "checkmark in deck builder and timed lobby" },
    { name: "InputFieldBackground", size: "32x32", desc: "just for the deck name" },
    { name: "UIMask", size: "32x32", desc: "deck editor background for where you pick cards from" },
    { name: "UISprite", size: "32x32", desc: "dropdowns, checkboxes and game select buttons" },
    { name: "audioOff", size: "50x50", desc: "/" },
    { name: "audioOn", size: "50x50", desc: "/" },
    { name: "musicOff", size: "50x50", desc: "/" },
    { name: "musicOn", size: "50x50", desc: "/" },
    { name: "Launch_bounty", size: "500x133", desc: "- transparency doesnt work" },
    { name: "MatchHistory", size: "500x133", desc: "- transparency doesnt work" },
    { name: "TCGMM_discord", size: "488x139", desc: "- transparency doesnt work" },
    { name: "PatronAsk", size: "1080x270", desc: "/" },
    { name: "ClydeBanner", size: "1500x500", desc: "ad banner - transparency doesnt work" },
    { name: "ImpactBanner", size: "1500x500", desc: "ad banner - transparency doesnt work" },
    { name: "CrossBanner", size: "1000x400", desc: "ad banner" },
];

const tbody = document.getElementById("textureTableBody");
const showMoreWrapper = document.getElementById("showMoreWrapper");
const showMoreBtn = document.getElementById("showMoreBtn");

let showingAll = false;
const initialDisplayCount = 7;

function renderTextures() {
    tbody.innerHTML = '';
    const displayCount = showingAll ? textures.length : initialDisplayCount;

    for (let i = 0; i < displayCount; i++) {
        const tex = textures[i];
        const tr = document.createElement("tr");
        tr.innerHTML = `
            <td class="checkbox-wrapper">
                <input type="checkbox" class="useTexture">
            </td>
            <td class="texture-name">${tex.name}</td>
            <td>
                <img class="preview" style="display: none;" />
            </td>
            <td class="desc">${tex.desc}</td>
            <td>
                <div class="file-input-wrapper">
                    <input type="file" accept="image/*" class="textureFile" id="file_${tex.name}">
                    <label for="file_${tex.name}" class="file-label">Choose File</label>
                    <span class="file-name"></span>
                </div>
            </td>
        `;
        tbody.appendChild(tr);

        const fileInput = tr.querySelector(".textureFile");
        const preview = tr.querySelector(".preview");
        const checkbox = tr.querySelector(".useTexture");
        const fileName = tr.querySelector(".file-name");

        // Load saved image if exists
        if (savedImages[tex.name]) {
            const saved = savedImages[tex.name];
            preview.src = saved.data;
            preview.style.display = "block";
            fileName.textContent = saved.name;
            checkbox.checked = true;
        }

        fileInput.addEventListener("change", () => {
            const file = fileInput.files[0];
            if (file) {
                fileName.textContent = file.name;
                const reader = new FileReader();
                reader.onload = e => {
                    checkbox.checked = true;
                    preview.src = e.target.result;
                    preview.style.display = "block";

                    // Save actual image data (base64) to localStorage
                    savedImages[tex.name] = {
                        name: file.name,
                        data: e.target.result,
                        type: file.type
                    };
                    saveToLocalStorage();
                };
                reader.readAsDataURL(file);
            } else {
                fileName.textContent = "";
                preview.src = "";
                preview.style.display = "none";

                // Remove from localStorage
                delete savedImages[tex.name];
                saveToLocalStorage();
            }
        });
    }

    // Update show more button
    if (textures.length > initialDisplayCount) {
        if (showingAll) {
            showMoreWrapper.style.display = 'none';
        } else {
            showMoreWrapper.style.display = 'block';
        }
    } else {
        showMoreWrapper.style.display = 'none';
    }
}

// Show more button handler
showMoreBtn.addEventListener('click', () => {
    showingAll = true;
    renderTextures();
});

// Initial render
renderTextures();

const statusMessage = document.getElementById("statusMessage");

function showStatus(message, isSuccess) {
    statusMessage.textContent = message;
    statusMessage.className = `status-message ${isSuccess ? 'success' : 'error'}`;
    statusMessage.style.display = 'block';
    setTimeout(() => {
        statusMessage.style.display = 'none';
    }, 5000);
}

document.getElementById("textureForm").addEventListener("submit", async (e) => {
    e.preventDefault();
    const formData = new FormData();
    let count = 0;

    tbody.querySelectorAll("tr").forEach((tr) => {
        const use = tr.querySelector(".useTexture").checked;
        const textureName = tr.cells[1].innerText;

        if (use && savedImages[textureName]) {
            // Convert base64 back to file for upload
            const saved = savedImages[textureName];
            const base64Data = saved.data.split(',')[1];
            const byteCharacters = atob(base64Data);
            const byteNumbers = new Array(byteCharacters.length);
            for (let i = 0; i < byteCharacters.length; i++) {
                byteNumbers[i] = byteCharacters.charCodeAt(i);
            }
            const byteArray = new Uint8Array(byteNumbers);
            const blob = new Blob([byteArray], { type: saved.type });
            const file = new File([blob], saved.name, { type: saved.type });

            formData.append("textures", file, textureName);
            count++;
        }
    });

    if (count === 0) {
        showStatus("Please select at least one texture to upload.", false);
        return;
    }

    try {
        const response = await fetch(api + "/full", {
            method: "POST",
            body: formData
        });

        if (!response.ok) {
            const errorText = await response.text();
            console.error("Upload failed", errorText);
            showStatus("Upload failed. Please try again.", false);
            return;
        }

        const blob = await response.blob();
        const url = window.URL.createObjectURL(blob);
        const a = document.createElement("a");
        a.href = url;
        a.download = "sharedassets1.assets";
        document.body.appendChild(a);
        a.click();
        a.remove();
        window.URL.revokeObjectURL(url);

        showStatus(`Successfully uploaded ${count} texture(s)!`, true);
    } catch (error) {
        console.error("Error:", error);
        showStatus("An error occurred during upload.", false);
    }
});