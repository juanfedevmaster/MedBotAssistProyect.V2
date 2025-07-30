using System;
using System.Collections.Generic;
using System.Linq;
using System.Text;
using System.Threading.Tasks;

namespace MedBotAssist.Models.DTOs
{
    public class ChatbotInteractionDto
    {
        public int InteractionId { get; set; }

        public int? UserId { get; set; }

        public DateTime? Timestamp { get; set; }

        public string? InteractionType { get; set; }

        public string? UserMessage { get; set; }

        public string? BotResponse { get; set; }

        public string? UserName { get; set; }
    }
}
