from ai.commentary.events import Event

COMMENTS = {
    "Coach": {
        Event.OPENING: [
            "Good start. Control the center early.",
            "Solid opening move. Develop your pieces next.",
        ],
        Event.GOOD_MOVE: [
            "Nice move. That improves your position.",
            "Well played. You are building an advantage.",
        ],
        Event.BRILLIANT_MOVE: [
            "Excellent! That is a genuinely strong move.",
            "Great find. That changes the position in your favor.",
        ],
        Event.BLUNDER: [
            "Careful, that move loses ground. Look for a safer option next time.",
            "That gives your opponent an opening. Watch your piece safety.",
        ],
        Event.CAPTURE: [
            "Good, you picked up some material there.",
            "Nice capture. Keep the pressure on.",
        ],
        Event.CAPTURE_QUEEN: [
            "Huge capture! Taking the queen is a major swing.",
            "That is a massive gain, well spotted.",
        ],
        Event.CAPTURE_ROOK: [
            "Good exchange, winning a rook is significant.",
            "Nice work picking up that rook.",
        ],
        Event.CHECK: [
            "Good, keep the pressure on the king.",
            "Nice check, look for the follow up.",
        ],
        Event.CHECKMATE: [
            "Checkmate! Well calculated from start to finish.",
            "That is checkmate, great game.",
        ],
        Event.STALEMATE: [
            "It is a stalemate, the game ends in a draw.",
        ],
        Event.PROMOTION: [
            "Nice, a new queen changes everything.",
            "Good promotion, that piece will help a lot now.",
        ],
    },
    "Competitive": {
        Event.OPENING: [
            "Let's go. I'm not holding back today.",
            "Opening moves. Get ready for a real fight.",
        ],
        Event.GOOD_MOVE: [
            "Not bad, but I've seen better.",
            "Okay, that was a decent try.",
        ],
        Event.BRILLIANT_MOVE: [
            "Whoa, okay, I did not expect that.",
            "That was actually really strong. Respect.",
        ],
        Event.BLUNDER: [
            "Ha, I'll take that.",
            "That's exactly the mistake I was hoping for.",
        ],
        Event.CAPTURE: [
            "Free material, thank you very much.",
            "Taking that piece without hesitation.",
        ],
        Event.CAPTURE_QUEEN: [
            "Your queen is mine now. Big moment.",
            "That's the queen. Game changing capture.",
        ],
        Event.CAPTURE_ROOK: [
            "Rook secured. I'm not giving it back.",
            "That rook is mine now.",
        ],
        Event.CHECK: [
            "Check. Your king isn't safe yet.",
            "Check, let's see how you handle this.",
        ],
        Event.CHECKMATE: [
            "Checkmate. That's how it's done.",
            "Game over. Good effort though.",
        ],
        Event.STALEMATE: [
            "Stalemate. Not the finish I wanted.",
        ],
        Event.PROMOTION: [
            "New queen, more firepower for me.",
            "Promotion complete. This changes everything.",
        ],
    },
    "Funny": {
        Event.OPENING: [
            "And we're off! Please don't blunder your queen in move 3.",
            "Let the chaos begin.",
        ],
        Event.GOOD_MOVE: [
            "Ooh, fancy. Someone's been practicing.",
            "That was smoother than my morning coffee.",
        ],
        Event.BRILLIANT_MOVE: [
            "Okay Magnus Carlsen, calm down.",
            "That move deserves its own highlight reel.",
        ],
        Event.BLUNDER: [
            "Oof. That one's going in the blooper reel.",
            "That move hurt me emotionally.",
        ],
        Event.CAPTURE: [
            "Nom nom, another piece down the hatch.",
            "Gone. Just like my will to resist snacks.",
        ],
        Event.CAPTURE_QUEEN: [
            "THE QUEEN?! Okay, drama level maximum.",
            "Queen captured. Someone alert the royal family.",
        ],
        Event.CAPTURE_ROOK: [
            "Rook secured. Castle privileges revoked.",
            "Another tower falls.",
        ],
        Event.CHECK: [
            "Check! Your king is sweating.",
            "Knock knock, it's check.",
        ],
        Event.CHECKMATE: [
            "Checkmate! Well, that escalated quickly.",
            "Game over. Time for a snack break.",
        ],
        Event.STALEMATE: [
            "Stalemate. Anticlimactic, but okay.",
        ],
        Event.PROMOTION: [
            "New queen just dropped.",
            "Promotion! Glow up complete.",
        ],
    },
}

FALLBACK_COMMENTS = {
    Event.OPENING: ["Good luck, have a great game."],
    Event.GOOD_MOVE: ["That's a solid move."],
    Event.BRILLIANT_MOVE: ["That's a brilliant move."],
    Event.BLUNDER: ["That move looks like a mistake."],
    Event.CAPTURE: ["A piece was captured."],
    Event.CAPTURE_QUEEN: ["The queen was captured."],
    Event.CAPTURE_ROOK: ["A rook was captured."],
    Event.CHECK: ["Check."],
    Event.CHECKMATE: ["Checkmate."],
    Event.STALEMATE: ["Stalemate."],
    Event.PROMOTION: ["A pawn was promoted."],
}
