let currentBrowserPath = "";
let currentInputField = "";

function closeFileBrowser() {
  document.getElementById("fileBrowserModal").classList.remove("show");
  document.body.style.overflow = "";
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

  const pathPreview = document.getElementById("pathPreview");
  if (pathPreview) {
    pathPreview.textContent = path;
  }

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
    folderList.innerHTML =
      '<div style="color: #666; text-align: center; padding: 20px;">No folders found in this location</div>';
    return;
  }

  const restrictedFolders = [
    "System Volume Information",
    "Python312",
    "OneDriveTemp",
    "$Recycle.Bin",
    "MinGW",
    "inetpub",
    "Recovery",
    "PerfLogs",
    "WindowsApps",
    "WpSystem",
    "Config.Msi",
    "MSOCache",
    "Intel",
    "AMD",
    "NVIDIA",
    "hiberfil.sys",
    "pagefile.sys",
    "swapfile.sys",
    "Windows",
    "Program Files",
    "Program Files (x86)",
    "ProgramData",
    "Boot",
    "EFI",
    "AppData",
    ".git",
    ".vs",
    ".vscode",
    "node_modules",
    "__pycache__",
    ".cache",
    ".temp",
    ".tmp",
  ];

  const filteredItems = items.filter((item) => {
    if (item.type === "parent") {
      return true;
    }

    const isRestricted = restrictedFolders.some(
      (restricted) =>
        item.name.toLowerCase() === restricted.toLowerCase() ||
        item.name.toLowerCase().startsWith(restricted.toLowerCase())
    );

    const isHidden = item.name.startsWith(".") && item.name !== "..";

    return !isRestricted && !isHidden;
  });

  if (filteredItems.length === 0) {
    folderList.innerHTML =
      '<div style="color: #666; text-align: center; padding: 20px;">No accessible folders found in this location</div>';
    return;
  }

  filteredItems.forEach((item) => {
    const folderItem = document.createElement("div");
    folderItem.className = "folder-item";

    if (item.type === "directory" || item.type === "parent") {
      folderItem.classList.add("folder-item-clickable");
      folderItem.innerHTML = `<span class="folder-icon">${item.icon}</span> <span class="folder-name">${item.name}</span> <span class="folder-hint">📂 Click to open</span>`;

      folderItem.addEventListener("click", function (e) {
        e.preventDefault();
        e.stopPropagation();
        browsePath(item.path);
      });
    } else {
      folderItem.classList.add("folder-item-file");
      folderItem.innerHTML = `<span class="folder-icon">${item.icon}</span> <span class="folder-name">${item.name}</span> <span class="file-hint">📄 File</span>`;
      folderItem.style.opacity = "0.6";
      folderItem.style.cursor = "default";
    }

    folderList.appendChild(folderItem);
  });
}

function goToDocuments() {
  fetch("/get_user_home")
    .then((response) => response.json())
    .then((data) => {
      if (data.home_path) {
        const documentsPath = data.home_path + "\\Documents";
        browsePath(documentsPath);
      }
    })
    .catch((error) => {
      console.log("Could not get Documents folder");
    });
}

function goToDownloads() {
  fetch("/get_user_home")
    .then((response) => response.json())
    .then((data) => {
      if (data.home_path) {
        const downloadsPath = data.home_path + "\\Downloads";
        browsePath(downloadsPath);
      }
    })
    .catch((error) => {
      console.log("Could not get Downloads folder");
    });
}

function goToDesktop() {
  fetch("/get_user_home")
    .then((response) => response.json())
    .then((data) => {
      if (data.home_path) {
        const desktopPath = data.home_path + "\\Desktop";
        browsePath(desktopPath);
      }
    })
    .catch((error) => {
      console.log("Could not get Desktop folder");
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

function openFileBrowser(inputFieldId) {
  currentInputField = inputFieldId;
  const modal = document.getElementById("fileBrowserModal");
  modal.classList.add("show");
  document.body.style.overflow = "hidden";
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

document.addEventListener("DOMContentLoaded", function () {
  const modal = document.getElementById("fileBrowserModal");
  if (modal) {
    modal.addEventListener("click", function (event) {
      if (event.target === this) {
        closeFileBrowser();
      }
    });

    const modalContent = modal.querySelector(".modal-content");
    if (modalContent) {
      modalContent.addEventListener("click", function (event) {
        event.stopPropagation();
      });
    }
  }
});
