// ==UserScript==
// @name         Lobby players
// @description  Get the list of players in the lobby and send to the server
// @version      0.0.2
// @author       You
// @license      MIT
// @match        https://www.geoguessr.com/*
// @grant        none
// ==/UserScript==

let members = [];

const originalSend = WebSocket.prototype.send;
WebSocket.prototype.send = function(...args) {
    const originalOnmessage = this.onmessage;
    this.onmessage = ({ data }) => {
        try {
            if (originalOnmessage) originalOnmessage({ data });
            const received = JSON.parse(data);
            if (received.code == 'PartyMemberListUpdated') {
                let payload = JSON.parse(received.payload);
                members = payload.members;
                console.log(`Number of members: ${members.length}`);
                console.log(JSON.stringify(members));
                
                // Send the member data to the Python server
                sendMembersToServer(members);
            }
        } catch (e) {
            console.error("Error processing WebSocket message:", e);
        }
    };
    return originalSend.call(this, ...args);
};

// Function to send the members' data to the Python server
function sendMembersToServer(members) {
    fetch('http://localhost:5000/lobby', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({ members })
    })
    .then(response => response.json())
    .then(data => {
        console.log("Data sent to server successfully:", data);
    })
    .catch(error => {
        console.error("Error sending data to server:", error);
    });
}
