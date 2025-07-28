using System;
using System.Collections.Generic;

namespace MedBotAssist.Models.Models
{

    public partial class Alert
    {
        public int AlertId { get; set; }

        public int? UserId { get; set; }

        public string? AlertType { get; set; }

        public string? Message { get; set; }

        public bool? IsRead { get; set; }

        public DateTime? AlertDate { get; set; }

        public virtual User? User { get; set; }
    }
}
