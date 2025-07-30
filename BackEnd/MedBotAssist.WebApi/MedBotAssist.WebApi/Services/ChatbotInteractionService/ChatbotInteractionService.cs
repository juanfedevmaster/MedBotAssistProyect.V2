using MedBotAssist.Interfaces;
using MedBotAssist.Models.DTOs;
using MedBotAssist.WebApi.Services.AuthService;
using Microsoft.EntityFrameworkCore;

namespace MedBotAssist.WebApi.Services.ChatbotInteractionService
{
    /// <summary>
    /// Service for handling chatbot interaction history operations.
    /// </summary>
    /// <remarks>
    /// Provides methods to retrieve chatbot conversation history for users.
    /// </remarks>
    public class ChatbotInteractionService : IChatbotInteractionService
    {
        private readonly IMedBotAssistDbContext _context;
        private readonly IUserService _userService;

        /// <summary>
        /// Initializes a new instance of the <see cref="ChatbotInteractionService"/> class.
        /// </summary>
        /// <param name="context">Database context for accessing chatbot interactions.</param>
        /// <param name="userService">Service for user-related operations.</param>
        public ChatbotInteractionService(IMedBotAssistDbContext context, IUserService userService)
        {
            _context = context;
            _userService = userService;
        }

        /// <summary>
        /// Retrieves the chatbot conversation history for a specific user and conversation.
        /// </summary>
        /// <param name="userName">The username of the user.</param>
        /// <param name="ConversationId">The unique identifier of the conversation.</param>
        /// <returns>
        /// A list of <see cref="ChatbotInteractionDto"/> representing the conversation history.
        /// </returns>
        /// <exception cref="ArgumentException">Thrown if the user is not found.</exception>
        public async Task<List<ChatbotInteractionDto>> GetChatBotHistory(string userName, string ConversationId)
        {
            var user = await _userService.GetUserByName(userName);
            if (user == null)
            {
                throw new ArgumentException("User not found");
            }

            var interactions = await _context.ChatbotInteractions
                .Where(ci => ci.UserId == user.UserId && ci.ConversationId == ConversationId)
                .Select(ci => new ChatbotInteractionDto
                {
                    InteractionId = ci.InteractionId,
                    UserMessage = ci.UserMessage,
                    BotResponse = ci.BotResponse,
                    Timestamp = ci.Timestamp,
                    UserId = ci.UserId,
                    UserName = user.UserName
                })
                .ToListAsync();

            return interactions;
        }
    }
}
