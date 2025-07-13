let statusInterval;
let currentBrowserPath = "";
let currentInputField = "";

function getCustomPath() {
  return document.getElementById("custom-path").value.trim();
}

function updatePathStatus() {
  const customPath = getCustomPath();
  const statusDiv = document.getElementById("custom-path-status");

  if (customPath) {
    statusDiv.innerHTML = `<span style="color: #27ae60;">✓ Using custom path: ${customPath}</span>`;
  } else {
    statusDiv.innerHTML = `<span style="color: #666;">Using default path: ${
      document.body.getAttribute("data-default-mkv-folder") || ""
    }</span>`;
  }
}

function selectCustomFolder() {
  currentInputField = "custom-path";
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

function clearCustomPath() {
  document.getElementById("custom-path").value = "";
  updatePathStatus();
  loadFiles();
}

function loadFiles() {
  const customPath = getCustomPath();
  const url = customPath
    ? `/files?path=${encodeURIComponent(customPath)}`
    : "/files";

  fetch(url)
    .then((response) => response.json())
    .then((data) => {
      const container = document.getElementById("files-container");
      if (data.error) {
        container.innerHTML = `<p style="color: red;">Error: ${data.error}</p>`;
        return;
      }

      if (data.files.length === 0) {
        const pathInfo = customPath
          ? `in "${customPath}"`
          : "in the configured folder";
        container.innerHTML = `<p>No MKV files found ${pathInfo}.</p>`;
        return;
      }

      const pathHeader = customPath
        ? `<div style="background: #e8f4fd; padding: 10px; border-radius: 4px; margin-bottom: 15px; font-size: 14px;">
          <strong>📁 Using custom path:</strong> ${customPath}
        </div>`
        : `<div style="background: #f8f9fa; padding: 10px; border-radius: 4px; margin-bottom: 15px; font-size: 14px;">
          <strong>📁 Using default path:</strong> ${
            window.DEFAULT_MKV_FOLDER || ""
          }
        </div>`;

      container.innerHTML =
        pathHeader +
        data.files
          .map(
            (file) => `
                  <div class="file-item">
                      <div class="file-info">
                          <div class="file-name">${file.name}</div>
                          <div class="file-details">
                              Series: ${file.series_title} | Episode: ${
              file.season_episode
            } | 
                              Size: ${(file.size / 1024 / 1024).toFixed(
                                1
                              )} MB | 
                              Modified: ${file.modified}
                          </div>
                      </div>
                  </div>
              `
          )
          .join("");
    })
    .catch((error) => {
      document.getElementById(
        "files-container"
      ).innerHTML = `<p style="color: red;">Error loading files: ${error.message}</p>`;
    });
}

function startProcessing() {
  const customPath = getCustomPath();
  const requestBody = customPath ? { custom_path: customPath } : {};

  fetch("/process", {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify(requestBody),
  })
    .then((response) => response.json())
    .then((data) => {
      if (data.error) {
        alert("Error: " + data.error);
        return;
      }

      document.getElementById("start-btn").style.display = "none";
      document.getElementById("stop-btn").style.display = "inline-block";
      document.getElementById("progress-container").style.display = "block";
      document.getElementById("log-container").style.display = "block";

      statusInterval = setInterval(updateStatus, 1000);
    })
    .catch((error) => {
      alert("Error starting processing: " + error.message);
    });
}

function stopProcessing() {
  fetch("/stop", { method: "POST" })
    .then((response) => response.json())
    .then((data) => {
      clearInterval(statusInterval);
      resetUI();
    });
}

function updateStatus() {
  fetch("/status")
    .then((response) => response.json())
    .then((status) => {
      const progressFill = document.getElementById("progress-fill");
      const progressText = document.getElementById("progress-text");
      const log = document.getElementById("log");

      if (status.total_files > 0) {
        const percentage = (status.progress / status.total_files) * 100;
        progressFill.style.width = percentage + "%";
        progressText.textContent = `Processing ${status.progress}/${status.total_files} files`;

        if (status.current_file) {
          progressText.textContent += ` - Current: ${status.current_file}`;
        }
      }

      log.innerHTML = status.log.map((entry) => `<div>${entry}</div>`).join("");
      log.scrollTop = log.scrollHeight;

      if (!status.is_running && status.progress > 0) {
        clearInterval(statusInterval);
        resetUI();
        progressText.textContent = "Processing completed!";
      }
    });
}

function resetUI() {
  document.getElementById("start-btn").style.display = "inline-block";
  document.getElementById("stop-btn").style.display = "none";
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
    updatePathStatus();
    loadFiles();
    closeFileBrowser();
  }
}

document.addEventListener("DOMContentLoaded", function () {
  updatePathStatus();
  loadFiles();

  document.getElementById("custom-path").addEventListener("input", function () {
    updatePathStatus();
  });

  document.getElementById("fileBrowserModal").onclick = function (event) {
    if (event.target === this) {
      closeFileBrowser();
    }
  };
});
