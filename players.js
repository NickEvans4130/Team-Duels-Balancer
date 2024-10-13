// ==UserScript==
// @name         Lobby players
// @description  Get the list of players in the lobby
// @version      0.0.1
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
                console.log(members.length);
                console.log(JSON.stringify(members))
                // member.nick, member.userId, member.team ("red" or "blue"), member.isPresent etc
            }
        } catch(e) {}
    };
    return originalSend.call(this, ...args);
};