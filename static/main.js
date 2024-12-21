document.getElementById("upButton").addEventListener("click", () => {
    fetch("/", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ type: "command", command: "go_up" })
    })
});

document.getElementById("downButton").addEventListener("click", () => {
    fetch("/", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ type: "command", command: "go_down" })
    });
});