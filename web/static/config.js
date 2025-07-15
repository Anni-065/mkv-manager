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
