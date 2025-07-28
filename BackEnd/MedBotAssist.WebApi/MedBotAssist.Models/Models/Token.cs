using System;
using System.Collections.Generic;

namespace MedBotAssist.Models.Models
{
    public partial class Token
    {
        public int TokenId { get; set; }

        public int? UserId { get; set; }

        public string JwtToken { get; set; } = null!;

        public DateTime ExpirationDate { get; set; }

        public bool? IsRevoked { get; set; }

        public DateTime? CreatedAt { get; set; }

        public DateTime? RevokedAt { get; set; }

        public virtual User? User { get; set; }
    }
}
