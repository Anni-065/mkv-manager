let statusInterval;
let droppedFiles = [];

function initializeDragAndDrop() {
  const dropZone = document.getElementById("dropZone");

  if (!dropZone) return;

  setupDropZoneClick();

  ["dragenter", "dragover", "dragleave", "drop"].forEach((eventName) => {
    document.addEventListener(eventName, preventDefaults, false);
    dropZone.addEventListener(eventName, preventDefaults, false);
  });

  function preventDefaults(e) {
    e.preventDefault();
    e.stopPropagation();
  }

  ["dragenter", "dragover"].forEach((eventName) => {
    dropZone.addEventListener(eventName, highlight, false);
  });

  ["dragleave", "drop"].forEach((eventName) => {
    dropZone.addEventListener(eventName, unhighlight, false);
  });

  function highlight() {
    dropZone.classList.add("drag-over");
  }

  function unhighlight() {
    dropZone.classList.remove("drag-over");
  }

  dropZone.addEventListener("drop", handleDrop, false);

  function handleDrop(e) {
    const dt = e.dataTransfer;

    if (dt.items) {
      const items = [...dt.items];
      let hasDirectories = false;

      for (let item of items) {
        if (item.webkitGetAsEntry) {
          const entry = item.webkitGetAsEntry();
          if (entry && entry.isDirectory) {
            hasDirectories = true;
            break;
          }
        }
      }

      if (hasDirectories) {
        handleDirectoryDrop(items);
        return;
      }
    }

    const files = dt.files;
    handleFiles(files);
  }
}

function setupDropZoneClick() {
  const dropZone = document.getElementById("dropZone");
  if (dropZone) {
    dropZone.addEventListener("click", function () {
      openFolderBrowserForDropZone();
    });
  }
}

function openFolderBrowserForDropZone() {
  currentInputField = "drop-zone-folder";
  const modal = document.getElementById("fileBrowserModal");
  modal.classList.add("show");
  document.body.style.overflow = "hidden";
  loadDrives();

  const defaultFolder = document.body.getAttribute("data-default-mkv-folder");
  if (defaultFolder) {
    browsePath(defaultFolder);
  } else {
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
}

function handleFiles(files) {
  const filesArray = [...files];
  let hasValidMkvFiles = false;
  let folderStructure = new Map();

  filesArray.forEach((file) => {
    const isFolder = file.type === "" && file.size % 4096 === 0;
    const isMkvFile =
      file.name.toLowerCase().endsWith(".mkv") ||
      (file.type === "" && file.name.toLowerCase().includes(".mkv"));

    if (file.webkitRelativePath) {
      const folderPath = file.webkitRelativePath.split("/")[0];

      if (!folderStructure.has(folderPath)) {
        folderStructure.set(folderPath, []);
      }

      folderStructure.get(folderPath).push(file);
    } else if (isMkvFile && !isFolder) {
      addDroppedItem(file.name, "mkv", formatFileSize(file.size), file.name);
      droppedFiles.push(file);
      hasValidMkvFiles = true;
    } else if (isFolder) {
      addDroppedItem(
        file.name,
        "folder",
        "Directory - Cannot access contents when dropped directly",
        file.name
      );

      if (!document.getElementById("folderDropWarning")) {
        showFolderDropWarning();
      }
    } else {
      addDroppedItem(file.name, "unknown", "Unsupported file type", file.name);
    }
  });

  folderStructure.forEach((files, folderName) => {
    const mkvFiles = files.filter(
      (file) =>
        file.name.toLowerCase().endsWith(".mkv") ||
        (file.type === "" && file.name.toLowerCase().includes(".mkv"))
    );

    if (mkvFiles.length > 0) {
      addDroppedItem(
        `📁 ${folderName}`,
        "folder",
        `Contains ${mkvFiles.length} MKV file(s)`,
        folderName
      );

      mkvFiles.forEach((file) => {
        addDroppedItem(
          `  └─ ${file.name}`,
          "mkv",
          formatFileSize(file.size),
          file.webkitRelativePath
        );

        droppedFiles.push(file);
        hasValidMkvFiles = true;
      });
    } else {
      addDroppedItem(
        `📁 ${folderName}`,
        "folder",
        "No MKV files found in this folder",
        folderName
      );

      if (!document.getElementById("folderDropWarning")) {
        showFolderDropWarning();
      }
    }
  });

  if (droppedFiles.length > 0 || document.querySelector(".dropped-file-item")) {
    document.getElementById("droppedFilesSection").style.display = "block";
  }
}

function showFolderDropWarning() {
  const droppedFilesList = document.getElementById("droppedFilesList");
  const warningDiv = document.createElement("div");
  warningDiv.id = "folderDropWarning";
  warningDiv.className = "folder-drop-warning";
  warningDiv.innerHTML = `
    <div style="background: #fff3cd; border: 1px solid #ffeaa7; border-radius: 8px; padding: 1rem; margin-bottom: 1rem; color: #856404;">
      <strong>📁 No MKV Files Found:</strong> The dropped folder(s) don't contain any MKV files to process.
      <br><strong>💡 Tip:</strong> Make sure your folder contains .mkv files, or use the "Browse" button to select a different folder.
    </div>
  `;
  droppedFilesList.insertBefore(warningDiv, droppedFilesList.firstChild);
}

function addDroppedItem(name, type, size, path) {
  const droppedFilesList = document.getElementById("droppedFilesList");
  const fileItem = document.createElement("div");
  fileItem.className = "dropped-file-item";

  const iconMap = {
    folder: "📁",
    mkv: "🎬",
    unknown: "❓",
  };

  const typeClassMap = {
    folder: "file-type-folder",
    mkv: "file-type-mkv",
    unknown: "file-type-unknown",
  };

  fileItem.innerHTML = `
    <div class="dropped-file-info">
      <div class="dropped-file-icon ${typeClassMap[type]}">${iconMap[type]}</div>
      <div class="dropped-file-details">
        <div class="dropped-file-name">${name}</div>
        <div class="dropped-file-path">${path}</div>
        <div class="dropped-file-size">${size}</div>
      </div>
    </div>
    <button class="dropped-file-remove" onclick="removeDroppedFile(this, '${name}')">
      ❌ Remove
    </button>
  `;

  droppedFilesList.appendChild(fileItem);
  updateDroppedFilesDisplay();
}

function removeDroppedFile(button, fileName) {
  droppedFiles = droppedFiles.filter((file) => file.name !== fileName);
  button.parentElement.remove();

  const remainingItems = document.querySelectorAll(".dropped-file-item");
  if (remainingItems.length === 0) {
    document.getElementById("droppedFilesSection").style.display = "none";
  }
  updateDroppedFilesDisplay();
}

function clearDroppedFiles() {
  droppedFiles = [];
  window.selectedFolderPath = null;
  document.getElementById("droppedFilesList").innerHTML = "";
  document.getElementById("droppedFilesSection").style.display = "none";

  const warningDiv = document.getElementById("folderDropWarning");
  if (warningDiv) {
    warningDiv.remove();
  }

  updateDroppedFilesDisplay();
}

function updateDroppedFilesDisplay() {
  const droppedFilesSection = document.getElementById("droppedFilesSection");
  const warningDiv = document.getElementById("folderDropWarning");

  const hasMkvFiles = droppedFiles.length > 0 || window.selectedFolderPath;
  const remainingItems = document.querySelectorAll(".dropped-file-item");

  if (hasMkvFiles) {
    droppedFilesSection.style.display = "block";
  }

  if (hasMkvFiles && warningDiv) {
    warningDiv.remove();
  }

  if (remainingItems.length === 0 && warningDiv) {
    warningDiv.remove();
  }
}

function formatFileSize(bytes) {
  if (bytes === 0) return "0 Bytes";
  const k = 1024;
  const sizes = ["Bytes", "KB", "MB", "GB"];
  const i = Math.floor(Math.log(bytes) / Math.log(k));
  return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + " " + sizes[i];
}

async function processDroppedFiles() {
  if (droppedFiles.length === 0 && !window.selectedFolderPath) {
    showNotification("No files to process!", "warning");
    return;
  }

  const processBtn =
    document.querySelector('button[onclick="processDroppedFiles()"]') ||
    document.getElementById("process-btn");
  if (processBtn) {
    processBtn.disabled = true;
    processBtn.textContent = "Processing...";
    processBtn.style.opacity = "0.6";
  }

  try {
    let response;

    if (droppedFiles.length > 0) {
      const formData = new FormData();

      droppedFiles.forEach((file, index) => {
        formData.append(`file_${index}`, file);
      });

      response = await fetch("/process_dropped_files", {
        method: "POST",
        body: formData,
      });
    } else if (window.selectedFolderPath) {
      const folderResponse = await fetch(
        `/files?path=${encodeURIComponent(window.selectedFolderPath)}`
      );
      const folderData = await folderResponse.json();

      if (folderData.error) {
        showNotification(
          "Error loading files from folder: " + folderData.error,
          "error"
        );

        if (processBtn) {
          processBtn.disabled = false;
          processBtn.textContent = "🎬 Process Files";
          processBtn.style.opacity = "1";
        }
        return;
      }

      if (folderData.files.length === 0) {
        showNotification(
          "No MKV files found in the selected folder.",
          "warning"
        );

        if (processBtn) {
          processBtn.disabled = false;
          processBtn.textContent = "🎬 Process Files";
          processBtn.style.opacity = "1";
        }
        return;
      }

      const filePaths = folderData.files.map(
        (file) => `${window.selectedFolderPath}\\${file.name}`
      );

      response = await fetch("/process_dropped_files", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({ files: filePaths }),
      });
    }

    const result = await response.json();

    if (result.error) {
      showNotification("Error: " + result.error, "error");

      if (processBtn) {
        processBtn.disabled = false;
        processBtn.textContent = "🎬 Process Files";
        processBtn.style.opacity = "1";
      }
      return;
    }

    clearDroppedFiles();
    window.selectedFolderPath = null;

    document.getElementById("stop-btn").style.display = "inline-block";
    document.getElementById("progress-container").style.display = "block";
    document.getElementById("log-container").style.display = "block";

    if (statusInterval) {
      clearInterval(statusInterval);
    }
    statusInterval = setInterval(updateStatus, 1000);

    showNotification("Processing started!", "success");
  } catch (error) {
    showNotification("Error processing files: " + error.message, "error");

    const processBtn =
      document.querySelector('button[onclick="processDroppedFiles()"]') ||
      document.getElementById("process-btn");

    if (processBtn) {
      processBtn.disabled = false;
      processBtn.textContent = "🎬 Process Files";
      processBtn.style.opacity = "1";
    }
  }
}

function stopProcessing() {
  fetch("/stop", { method: "POST" })
    .then((response) => response.json())
    .then((data) => {
      clearInterval(statusInterval);
      document.getElementById("stop-btn").style.display = "none";

      const processBtn =
        document.querySelector('button[onclick="processDroppedFiles()"]') ||
        document.getElementById("process-btn");
      if (processBtn) {
        processBtn.disabled = false;
        processBtn.textContent = "🎬 Process Files";
        processBtn.style.opacity = "1";
      }
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

      if (!status.is_running) {
        clearInterval(statusInterval);
        document.getElementById("stop-btn").style.display = "none";

        const processBtn =
          document.querySelector('button[onclick="processDroppedFiles()"]') ||
          document.getElementById("process-btn");
        if (processBtn) {
          processBtn.disabled = false;
          processBtn.textContent = "🎬 Process Files";
          processBtn.style.opacity = "1";
        }

        if (status.progress > 0) {
          progressText.textContent = "Processing completed!";
        } else {
          progressText.textContent = "Processing stopped.";
        }
      }
    });
}

function selectCurrentFolder() {
  if (currentBrowserPath && currentInputField) {
    if (currentInputField === "drop-zone-folder") {
      loadFilesFromFolderForDropZone(currentBrowserPath);
      closeFileBrowser();
    }
  }
}

function loadFilesFromFolderForDropZone(folderPath) {
  fetch(`/files?path=${encodeURIComponent(folderPath)}`)
    .then((response) => response.json())
    .then((data) => {
      if (data.error) {
        showNotification(
          "Error loading files from folder: " + data.error,
          "error"
        );
        return;
      }

      if (data.files.length === 0) {
        showNotification(
          "No MKV files found in the selected folder.",
          "warning"
        );
        return;
      }

      clearDroppedFiles();

      data.files.forEach((file) => {
        addDroppedItem(
          file.name,
          "mkv",
          `${(file.size / 1024 / 1024).toFixed(1)} MB`,
          `${folderPath}\\${file.name}`
        );
      });

      document.getElementById("droppedFilesSection").style.display = "block";
      window.selectedFolderPath = folderPath;

      showNotification(
        `Added ${data.files.length} MKV files from the selected folder!`,
        "success"
      );
    })
    .catch((error) => {
      showNotification("Error loading files: " + error.message, "error");
    });
}

function showNotification(message, type = "info") {
  const existingNotification = document.querySelector(".notification");

  if (existingNotification) {
    existingNotification.remove();
  }

  const notification = document.createElement("div");
  notification.className = `notification notification-${type}`;
  notification.textContent = message;

  notification.style.cssText = `
    position: fixed;
    top: 20px;
    right: 20px;
    padding: 15px 20px;
    border-radius: 5px;
    color: white;
    font-weight: bold;
    z-index: 10000;
    max-width: 300px;
    word-wrap: break-word;
    transition: opacity 0.3s ease;
  `;

  const colors = {
    success: "#28a745",
    error: "#dc3545",
    warning: "#ffc107",
    info: "#17a2b8",
  };

  notification.style.backgroundColor = colors[type] || colors.info;
  if (type === "warning") {
    notification.style.color = "#000";
  }

  document.body.appendChild(notification);

  setTimeout(() => {
    if (notification && notification.parentNode) {
      notification.style.opacity = "0";
      setTimeout(() => {
        if (notification && notification.parentNode) {
          notification.remove();
        }
      }, 300);
    }
  }, 5000);
}

document.addEventListener("DOMContentLoaded", function () {
  initializeDragAndDrop();
  setupDropZoneClick();
});

window.addEventListener("beforeunload", function () {
  if (statusInterval) {
    clearInterval(statusInterval);
  }
});

async function handleDirectoryDrop(items) {
  const allFiles = [];
  const folderStructure = new Map();

  for (let item of items) {
    if (item.webkitGetAsEntry) {
      const entry = item.webkitGetAsEntry();
      if (entry) {
        if (entry.isDirectory) {
          const files = await readDirectoryRecursively(entry);

          files.forEach((fileInfo) => {
            allFiles.push(fileInfo.file);
            const folderName = entry.name;

            if (!folderStructure.has(folderName)) {
              folderStructure.set(folderName, []);
            }

            folderStructure.get(folderName).push(fileInfo.file);
          });
        } else if (entry.isFile) {
          entry.file((file) => {
            allFiles.push(file);
          });
        }
      }
    }
  }

  if (allFiles.length > 0) {
    processDirectoryFiles(folderStructure);
  }
}

function readDirectoryRecursively(dirEntry, path = "") {
  return new Promise((resolve) => {
    const dirReader = dirEntry.createReader();
    const files = [];

    function readEntries() {
      dirReader.readEntries((entries) => {
        if (entries.length === 0) {
          resolve(files);
          return;
        }

        const promises = entries.map((entry) => {
          const fullPath = path ? `${path}/${entry.name}` : entry.name;

          if (entry.isFile) {
            return new Promise((fileResolve) => {
              entry.file((file) => {
                Object.defineProperty(file, "webkitRelativePath", {
                  value: fullPath,
                  writable: false,
                });
                files.push({ file, path: fullPath });
                fileResolve();
              });
            });
          } else if (entry.isDirectory) {
            return readDirectoryRecursively(entry, fullPath).then(
              (subFiles) => {
                files.push(...subFiles);
              }
            );
          }
          return Promise.resolve();
        });

        Promise.all(promises).then(() => {
          readEntries();
        });
      });
    }

    readEntries();
  });
}

function processDirectoryFiles(folderStructure) {
  folderStructure.forEach((files, folderName) => {
    const mkvFiles = files.filter(
      (file) =>
        file.name.toLowerCase().endsWith(".mkv") ||
        (file.type === "" && file.name.toLowerCase().includes(".mkv"))
    );

    if (mkvFiles.length > 0) {
      addDroppedItem(
        `📁 ${folderName}`,
        "folder",
        `Contains ${mkvFiles.length} MKV file(s)`,
        folderName
      );

      mkvFiles.forEach((file) => {
        addDroppedItem(
          `  └─ ${file.name}`,
          "mkv",
          formatFileSize(file.size),
          file.webkitRelativePath || file.name
        );
        droppedFiles.push(file);
      });

      const warningDiv = document.getElementById("folderDropWarning");
      if (warningDiv) {
        warningDiv.remove();
      }
    } else {
      addDroppedItem(
        `📁 ${folderName}`,
        "folder",
        "No MKV files found in this folder",
        folderName
      );
      if (!document.getElementById("folderDropWarning")) {
        showFolderDropWarning();
      }
    }
  });

  if (droppedFiles.length > 0 || document.querySelector(".dropped-file-item")) {
    document.getElementById("droppedFilesSection").style.display = "block";
  }
}
