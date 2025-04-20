document.getElementById("upload-form").addEventListener("submit", function(event) {
    event.preventDefault();

    let fileInput = document.getElementById("image-upload");
    if (fileInput.files.length === 0) {
        alert("Vui lòng chọn một ảnh!");
        return;
    }

    let formData = new FormData();
    formData.append("image", fileInput.files[0]);

    document.getElementById("loading").classList.remove("hidden");
    document.getElementById("result").classList.add("hidden");

    fetch("/upload", {
        method: "POST",
        body: formData
    })
    .then(response => response.json())
    .then(data => {
        document.getElementById("loading").classList.add("hidden");

        if (data.error) {
            alert(data.error);
            return;
        }

        document.getElementById("original-image").src = data.original_url;
        document.getElementById("output-image").src = data.image_url;
        document.getElementById("result").classList.remove("hidden");

        let countResultDiv = document.getElementById("count-result");
        if (Object.keys(data.counts).length === 0) {
            countResultDiv.innerHTML = `<p style='color: red;'>⚠️ Không phát hiện côn trùng trong ảnh!</p>`;
        } else {
            countResultDiv.innerHTML = "<h3>Số lượng phát hiện:</h3>";
            for (let [key, value] of Object.entries(data.counts)) {
                countResultDiv.innerHTML += `<p><strong>🦟 ${key}: <b>${value}</b> con</strong></p>`;
                countResultDiv.innerHTML += `<div style="text-align: justify;"><strong>Thông tin loài:</strong> ${data.insect_details[key]}</div>`;
            }
        }

        document.getElementById("download-link").href = data.image_url;
    })
    .catch(error => {
        document.getElementById("loading").classList.add("hidden");
        console.error("Lỗi:", error);
    });
});

document.getElementById("upload-video-form").addEventListener("submit", function(event) {
    event.preventDefault();

    let fileInput = document.getElementById("video-upload");
    if (fileInput.files.length === 0) {
        alert("Vui lòng chọn một video!");
        return;
    }

    let formData = new FormData();
    formData.append("video", fileInput.files[0]);

    document.getElementById("loading-video").classList.remove("hidden");
    document.getElementById("video-result").classList.add("hidden");

    fetch("/upload_video", {
        method: "POST",
        body: formData
    })
    .then(response => response.json())
    .then(data => {
        document.getElementById("loading-video").classList.add("hidden");

        if (data.error) {
            alert(data.error);
            return;
        }

        document.getElementById("original-video").src = data.original_url;
        document.getElementById("download-video-link").href = data.video_url;
        document.getElementById("video-result").classList.remove("hidden");

        let countResultDiv = document.getElementById("count-result-video");
        if (Object.keys(data.counts).length === 0) {
            countResultDiv.innerHTML = `<p style='color: red;'>⚠️ Không phát hiện côn trùng trong video!</p>`;
        } else {
            countResultDiv.innerHTML = "<h3>Số lượng phát hiện:</h3>";
            for (let [key, value] of Object.entries(data.counts)) {
                countResultDiv.innerHTML += `<p><strong>🦟 ${key}: <b>${value}</b> con</strong></p>`;
                countResultDiv.innerHTML += `<div style="text-align: justify;"><strong>Thông tin loài:</strong> ${data.insect_details[key]}</div>`;
            }
        }
    })
    .catch(error => {
        document.getElementById("loading-video").classList.add("hidden");
        console.error("Lỗi:", error);
    });
});