let statusInterval;
let droppedFiles = [];
let isProcessingDrop = false;

function initializeDragAndDrop() {
  const dropZone = document.getElementById("dropZone");

  if (!dropZone) return;

  setupDropZoneClick();

  isProcessingDrop = false;

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

    if (isProcessingDrop) {
      return;
    }

    isProcessingDrop = true;

    setTimeout(() => {
      if (isProcessingDrop) {
        isProcessingDrop = false;
      }
    }, 10000);

    droppedFiles = [];
    document.getElementById("droppedFilesList").innerHTML = "";

    if (dt.items && dt.items.length > 0) {
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
        handleDirectoryDrop(items).finally(() => {
          isProcessingDrop = false;
        });
      } else {
        const files = dt.files;
        handleFiles(files);
        isProcessingDrop = false;
      }
    } else if (dt.files && dt.files.length > 0) {
      const files = dt.files;
      handleFiles(files);
      isProcessingDrop = false;
    } else {
      isProcessingDrop = false;
    }
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
  const processingId = Math.random().toString(36).substr(2, 9);
  console.log("=== HANDLE FILES START ===", processingId);
  console.log("Files count:", files.length);

  resetProcessingToIdle();

  document.getElementById("droppedFilesList").innerHTML = "";
  droppedFiles = [];

  const filesArray = [...files];
  let hasValidMkvFiles = false;
  let folderStructure = new Map();

  filesArray.forEach((file, index) => {
    console.log(
      `Processing file ${index + 1} in session ${processingId}:`,
      file.name,
      file.type,
      file.size
    );
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
      console.log("Adding MKV file in session", processingId, ":", file.name);
      addDroppedItem(
        file.name,
        "mkv",
        formatFileSize(file.size),
        "📁 Dropped file"
      );
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
    unknown: "❌",
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
    processBtn.textContent = "🚀 Starting...";
    processBtn.style.opacity = "0.7";
  }

  const processingIdle = document.getElementById("processing-idle");
  const processingActive = document.getElementById("processing-active");
  const progressContainer = document.getElementById("progress-container");
  const logContainer = document.getElementById("log-container");
  const stopBtn = document.getElementById("stop-btn");

  processingIdle.style.display = "none";
  processingActive.style.display = "block";
  progressContainer.style.display = "block";
  logContainer.style.display = "block";
  stopBtn.style.display = "inline-block";

  const progressFill = document.getElementById("progress-fill");
  const progressText = document.getElementById("progress-text");
  const log = document.getElementById("log");

  progressFill.style.width = "0%";
  progressText.textContent = "Initializing processing...";
  log.innerHTML = "<div>🚀 Starting processing...</div>";

  try {
    let response;

    if (droppedFiles.length > 0) {
      const formData = new FormData();

      droppedFiles.forEach((file, index) => {
        formData.append(`file_${index}`, file);
      });

      log.innerHTML += "<div>📤 Uploading files...</div>";
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
        resetProcessingToIdle();
        return;
      }

      if (folderData.files.length === 0) {
        showNotification(
          "No MKV files found in the selected folder.",
          "warning"
        );
        resetProcessingToIdle();
        return;
      }

      const filePaths = folderData.files.map(
        (file) => `${window.selectedFolderPath}\\${file.name}`
      );

      log.innerHTML += "<div>📁 Processing folder contents...</div>";
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
      resetProcessingToIdle();
      return;
    }

    clearDroppedFiles();
    window.selectedFolderPath = null;

    log.innerHTML += "<div>✅ Processing started successfully!</div>";
    log.scrollTop = log.scrollHeight;

    if (statusInterval) {
      clearInterval(statusInterval);
    }
    statusInterval = setInterval(updateStatus, 500);

    showNotification("Processing started!", "success");
  } catch (error) {
    showNotification("Error processing files: " + error.message, "error");
    resetProcessingToIdle();
  }
}

function resetToIdleState() {
  const processingIdle = document.getElementById("processing-idle");
  const processingActive = document.getElementById("processing-active");

  if (processingIdle && processingActive) {
    processingIdle.style.display = "block";
    processingActive.style.display = "none";
  }

  if (statusInterval) {
    clearInterval(statusInterval);
    statusInterval = null;
  }

  resetProcessButton();
}

function resetProcessButton() {
  const processBtn =
    document.querySelector('button[onclick="processDroppedFiles()"]') ||
    document.getElementById("process-btn");

  if (processBtn) {
    processBtn.disabled = false;
    processBtn.textContent = "🚀 Process Files";
    processBtn.style.opacity = "1";
  }
}

function resetProcessingToIdle() {
  const processingIdle = document.getElementById("processing-idle");
  const processingActive = document.getElementById("processing-active");

  processingIdle.style.display = "block";
  processingActive.style.display = "none";

  resetProcessButton();
}

function stopProcessing() {
  fetch("/stop", { method: "POST" })
    .then((response) => response.json())
    .then((data) => {
      if (statusInterval) {
        clearInterval(statusInterval);
        statusInterval = null;
      }

      const processingIdle = document.getElementById("processing-idle");
      const processingActive = document.getElementById("processing-active");

      processingIdle.style.display = "block";
      processingActive.style.display = "none";

      resetProcessButton();
      showNotification("Processing stopped by user", "info");
    })
    .catch((error) => {
      console.error("Error stopping processing:", error);
      showNotification("Error stopping processing", "error");
    });
}

function updateStatus() {
  fetch("/status")
    .then((response) => response.json())
    .then((status) => {
      const progressFill = document.getElementById("progress-fill");
      const progressText = document.getElementById("progress-text");
      const log = document.getElementById("log");
      const processingIdle = document.getElementById("processing-idle");
      const processingActive = document.getElementById("processing-active");
      const progressContainer = document.getElementById("progress-container");
      const logContainer = document.getElementById("log-container");
      const stopBtn = document.getElementById("stop-btn");

      if (status.is_running) {
        processingIdle.style.display = "none";
        processingActive.style.display = "block";
        progressContainer.style.display = "block";
        logContainer.style.display = "block";
        stopBtn.style.display = "inline-block";

        if (status.total_files > 0) {
          const percentage = (status.progress / status.total_files) * 100;
          progressFill.style.width = percentage + "%";
          progressText.textContent = `Processing ${status.progress}/${status.total_files} files`;

          if (status.current_file) {
            progressText.textContent += ` - Current: ${status.current_file}`;
          }
        } else {
          progressFill.style.width = "0%";
          progressText.textContent = "Preparing to process files...";
        }

        log.innerHTML = status.log
          .map((entry) => `<div>${entry}</div>`)
          .join("");
        log.scrollTop = log.scrollHeight;
      } else {
        processingIdle.style.display = "none";
        processingActive.style.display = "block";
        progressContainer.style.display = "block";
        logContainer.style.display = "block";
        stopBtn.style.display = "none";

        if (status.total_files > 0) {
          const percentage = (status.progress / status.total_files) * 100;
          progressFill.style.width = percentage + "%";

          if (status.progress === status.total_files) {
            progressText.textContent = `✅ Processing completed! ${status.progress}/${status.total_files} files processed`;
          } else {
            progressText.textContent = `⏸️ Processing stopped at ${status.progress}/${status.total_files} files`;
          }
        } else {
          progressFill.style.width = "0%";
          progressText.textContent = "Processing finished";
        }

        if (status.log && status.log.length > 0) {
          log.innerHTML = status.log
            .map((entry) => `<div>${entry}</div>`)
            .join("");
          log.scrollTop = log.scrollHeight;
        }

        if (statusInterval) {
          clearInterval(statusInterval);
          statusInterval = null;
        }

        resetProcessButton();

        if (status.progress > 0) {
          showNotification("Processing completed successfully!", "success");
        }
      }
    })
    .catch((error) => {
      console.error("Error fetching status:", error);

      if (statusInterval) {
        clearInterval(statusInterval);
        statusInterval = null;
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
  resetProcessingToIdle();

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

      window.selectedFolderPath = folderPath;
      droppedFiles = [];
      document.getElementById("droppedFilesList").innerHTML = "";

      addDroppedItem(
        `📁 ${folderPath}`,
        "folder",
        `Contains ${data.files.length} MKV file(s)`,
        folderPath
      );

      data.files.forEach((file) => {
        addDroppedItem(
          `  └─ ${file.name}`,
          "mkv",
          formatFileSize(file.size),
          `${folderPath}\\${file.name}`
        );
      });

      document.getElementById("droppedFilesSection").style.display = "block";
      updateDroppedFilesDisplay();

      showNotification(
        `Loaded ${data.files.length} MKV files from folder`,
        "success"
      );
    })
    .catch((error) => {
      console.error("Error loading files from folder:", error);
      showNotification("Error loading files from folder", "error");
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
  initializeProcessingState();
});

function initializeProcessingState() {
  fetch("/status")
    .then((response) => response.json())
    .then((status) => {
      if (status.is_running) {
        updateStatus();
      } else {
        resetProcessingToIdle();
      }
    })
    .catch((error) => {
      console.error("Error fetching initial status:", error);
      resetProcessingToIdle();
    });
}

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
