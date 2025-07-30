using MedBotAssist.Models.DTOs;
using System.Collections.Generic;
using System.Threading.Tasks;

namespace MedBotAssist.Interfaces
{
    public interface IChatbotInteractionService
    {
        Task<List<ChatbotInteractionDto>> GetChatBotHistory(string userName, string ConversationId);
    }
}
