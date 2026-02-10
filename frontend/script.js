const threads = [
    { name: "Mom", preview: "Dinner at 8?", spam: false },
    { name: "Bank Alert", preview: "Your account is suspended", spam: true },
    { name: "John", preview: "Check this out!", spam: false },
    { name: "Unknown", preview: "You've won a prize!", spam: true },
];

const threadList = document.getElementById("thread-list");
const messagesView = document.getElementById("messages");
const contactName = document.getElementById("contact-name");

function renderThreads(filterSpam = false) {
    threadList.innerHTML = "";
    threads
        .filter((t) => (filterSpam ? t.spam : !t.spam))
        .forEach((t, i) => {
            const div = document.createElement("div");
            div.className = "thread";
            div.textContent = `${t.name}: ${t.preview}`;
            div.onclick = () => openConversation(t.name);
            threadList.appendChild(div);
        });
}

function openConversation(name) {
    contactName.textContent = name;
    messagesView.innerHTML = `
    <div class="message received">Hey ${name}, what's up?</div>
    <div class="message sent">Just checking in!</div>
  `;
}

document.getElementById("spam-tab").onclick = () => renderThreads(true);
renderThreads();

document.getElementById("send-btn").onclick = () => {
    const input = document.getElementById("reply-input");
    if (input.value.trim()) {
        const msg = document.createElement("div");
        msg.className = "message sent";
        msg.textContent = input.value;
        messagesView.appendChild(msg);
        input.value = "";
    }
};