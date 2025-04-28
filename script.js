// Preview uploaded image
function previewFile() {
    const input = document.getElementById("imageInput");
    const file = input.files[0];
    const preview = document.getElementById("previewImage");

    if (file) {
        const reader = new FileReader();
        reader.onload = (e) => {
            preview.src = e.target.result;
        };
        reader.readAsDataURL(file);
    }
}

// Upload image and get analysis (scene, objects, colors)
function uploadImage() {
    const input = document.getElementById("imageInput");
    const file = input.files[0];

    if (!file) {
        alert("Please select an image first.");
        return;
    }

    const formData = new FormData();
    formData.append("image", file);

    fetch("/process", {
        method: "POST",
        body: formData
    })
    .then(response => response.json())
    .then(data => {
        if (data.error) {
            alert(data.error);
            return;
        }

        // Show results
        document.getElementById("result").style.display = "block";
        document.getElementById("uploadedImage").src = data.image_url;
        document.getElementById("objects").innerText = data.objects.join(", ");
        document.getElementById("scene").innerText = data.scene;
        document.getElementById("colors").innerText = data.colors.join(", ");
    })
    .catch(error => {
        console.error("Error:", error);
        alert("Something went wrong. Please try again.");
    });
}

// Smooth scroll on "Try Now" button
document.querySelector(".try-now").addEventListener("click", function(event) {
    event.preventDefault();
    document.querySelector(".upload").scrollIntoView({ behavior: "smooth" });
});

// Generate music based on uploaded image
async function generateMusic() {
    const input = document.getElementById("imageInput");
    const loader = document.getElementById("loader");
    const audio = document.getElementById("audioPlayer");
    const button = document.getElementById("generateBtn");

    if (!input.files[0]) {
        alert("Please upload an image first.");
        return;
    }

    const formData = new FormData();
    formData.append("image", input.files[0]);

    // Show loader and disable button
    loader.style.display = "block";
    button.disabled = true;
    button.innerText = "Generating...";

    try {
        const response = await fetch("/generate-music", {
            method: "POST",
            body: formData
        });

        const data = await response.json();

        if (data.success && data.audio_url) {
            audio.src = data.audio_url;
            audio.style.display = "block";
            audio.play();
        } else {
            alert("Error generating music. Please try again.");
        }
    } catch (error) {
        console.error("Music generation error:", error);
        alert("An error occurred while generating music.");
    } finally {
        loader.style.display = "none";
        button.disabled = false;
        button.innerText = "Generate Music";
    }
}
