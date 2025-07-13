// MKV Cleaner - Configuration Page JavaScript

let currentBrowserPath = "";
let currentInputField = "";

function openFileBrowser(inputFieldId) {
  currentInputField = inputFieldId;
  document.getElementById("fileBrowserModal").style.display = "block";
  loadDrives();

  fetch("/get_user_home")
    .then((response) => response.json())
    .then((data) => {
      if (data.home_path) {
        browsePath(data.home_path);
      } else {
        browsePath("C:\\Users");
      }
    })
    .catch((error) => {
      console.log("Could not get user home, using default");
      browsePath("C:\\Users");
    });
}

function closeFileBrowser() {
  document.getElementById("fileBrowserModal").style.display = "none";
}

function loadDrives() {
  fetch("/get_drives")
    .then((response) => response.json())
    .then((data) => {
      const driveSelector = document.getElementById("driveSelector");
      driveSelector.innerHTML = "";

      if (data.error) {
        document.getElementById("folderList").innerHTML =
          '<div style="color: red;">Error loading drives: ' +
          data.error +
          "</div>";
        return;
      }

      data.drives.forEach((drive) => {
        const option = document.createElement("option");
        option.value = drive.path;
        option.textContent = `${drive.letter}: (${formatBytes(
          drive.free
        )} free)`;
        driveSelector.appendChild(option);
      });
      if (data.drives.length > 0) {
        changeDrive();
      }
    })
    .catch((error) => {
      console.error("Error loading drives:", error);
      document.getElementById("folderList").innerHTML =
        '<div style="color: red;">Error loading drives</div>';
    });
}

function formatBytes(bytes) {
  if (bytes === 0) return "0 Bytes";
  const k = 1024;
  const sizes = ["Bytes", "KB", "MB", "GB", "TB"];
  const i = Math.floor(Math.log(bytes) / Math.log(k));
  return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + " " + sizes[i];
}

function changeDrive() {
  const selectedDrive = document.getElementById("driveSelector").value;
  if (selectedDrive) {
    browsePath(selectedDrive);
  }
}

function browsePath(path) {
  currentBrowserPath = path;
  document.getElementById("currentPath").textContent = path;

  fetch(`/browse?path=${encodeURIComponent(path)}`)
    .then((response) => response.json())
    .then((data) => {
      if (data.error) {
        document.getElementById("folderList").innerHTML =
          '<div style="color: red;">Error: ' + data.error + "</div>";
        return;
      }
      displayFolders(data.items);
    })
    .catch((error) => {
      console.error("Error browsing path:", error);
      document.getElementById("folderList").innerHTML =
        '<div style="color: red;">Error loading folders</div>';
    });
}

function displayFolders(items) {
  const folderList = document.getElementById("folderList");
  folderList.innerHTML = "";

  if (!items || items.length === 0) {
    folderList.innerHTML = '<div style="color: #666;">No folders found</div>';
    return;
  }

  items.forEach((item) => {
    const folderItem = document.createElement("div");
    folderItem.className = "folder-item";
    folderItem.innerHTML = `<span class="folder-icon">${item.icon}</span> ${item.name}`;

    if (item.type === "directory" || item.type === "parent") {
      folderItem.onclick = function () {
        browsePath(item.path);
      };
    } else {
      folderItem.style.opacity = "0.7";
      folderItem.style.cursor = "default";
    }

    folderList.appendChild(folderItem);
  });
}

function goToParentFolder() {
  if (currentBrowserPath) {
    const pathParts = currentBrowserPath.split("\\\\");
    if (pathParts.length > 1) {
      pathParts.pop();
      const parentPath = pathParts.join("\\\\");
      if (parentPath) {
        browsePath(parentPath);
      }
    }
  }
}

function refreshCurrentFolder() {
  if (currentBrowserPath) {
    browsePath(currentBrowserPath);
  }
}

function selectCurrentFolder() {
  if (currentBrowserPath && currentInputField) {
    document.getElementById(currentInputField).value = currentBrowserPath;
    closeFileBrowser();
  }
}

function openExplorer(inputFieldId) {
  const path = document.getElementById(inputFieldId).value;
  if (path) {
    fetch("/open_explorer", {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify({ path: path }),
    })
      .then((response) => response.json())
      .then((data) => {
        if (data.success) {
          alert("📂 Windows Explorer opened successfully!");
        } else {
          alert("❌ Error opening Windows Explorer: " + data.error);
        }
      })
      .catch((error) => {
        console.error("Error opening explorer:", error);
        alert("❌ Error opening Windows Explorer");
      });
  } else {
    alert("⚠️ Please enter a path first");
  }
}

// Initialize the configuration page when DOM is loaded
document.addEventListener("DOMContentLoaded", function () {
  // Close modal when clicking outside
  document.getElementById("fileBrowserModal").onclick = function (event) {
    if (event.target === this) {
      closeFileBrowser();
    }
  };
});
