using MedBotAssist.Interfaces;
using MedBotAssist.WebApi.Services.AuthService;
using Microsoft.AspNetCore.Http;
using Microsoft.AspNetCore.Mvc;

namespace MedBotAssist.WebApi.Controllers
{
    /// <summary>
    /// API controller for managing chatbot interaction history.
    /// </summary>
    /// <remarks>
    /// Provides endpoints to retrieve the conversation history between a user and the chatbot.
    /// </remarks>
    [Route("api/[controller]")]
    [ApiController]
    public class ChatbotInteractionController : ControllerBase
    {
        private readonly IChatbotInteractionService _chatbotInteractionService;

        /// <summary>
        /// Initializes a new instance of the <see cref="ChatbotInteractionController"/> class.
        /// </summary>
        /// <param name="chatbotInteractionService">Service for chatbot interaction operations.</param>
        public ChatbotInteractionController(IChatbotInteractionService chatbotInteractionService)
        {
            _chatbotInteractionService = chatbotInteractionService;
        }

        /// <summary>
        /// Retrieves the chatbot conversation history for a specific user and conversation.
        /// </summary>
        /// <param name="userName">The username of the user.</param>
        /// <param name="conversationId">The unique identifier of the conversation.</param>
        /// <returns>
        /// Returns 200 OK with the conversation history if found,
        /// 400 Bad Request if parameters are missing,
        /// 404 Not Found if the conversation does not exist,
        /// or 500 Internal Server Error for unexpected errors.
        /// </returns>
        [HttpGet("getHistory")]
        [HasPermission("UseAgent")]
        public async Task<IActionResult> GetChatBotHistory(string userName, string conversationId)
        {
            var userNameClaim = JwtClaimHelper.GetUsernameClaim(HttpContext.User, "name");

            if (userNameClaim != null && !userNameClaim.Equals(userName))
            {
                return BadRequest("User name from token does not match the provided user name.");
            }

            if (string.IsNullOrEmpty(userName) || string.IsNullOrEmpty(conversationId))
            {
                return BadRequest("User name and conversation ID cannot be null or empty.");
            }

            try
            {
                var history = await _chatbotInteractionService.GetChatBotHistory(userName, conversationId);
                return Ok(history);
            }
            catch (ArgumentException ex)
            {
                return NotFound(ex.Message);
            }
            catch (Exception ex)
            {
                return StatusCode(StatusCodes.Status500InternalServerError, ex.Message);
            }
        }
    }
}
