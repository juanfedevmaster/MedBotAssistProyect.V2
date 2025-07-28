using System;
using System.Collections.Generic;

namespace MedBotAssist.Models.Models
{
    public partial class ChatbotInteraction
    {
        public int InteractionId { get; set; }

        public int? UserId { get; set; }

        public DateTime? Timestamp { get; set; }

        public string? InteractionType { get; set; }

        public string? UserMessage { get; set; }

        public string? BotResponse { get; set; }

        public virtual User? User { get; set; }
    }
}
