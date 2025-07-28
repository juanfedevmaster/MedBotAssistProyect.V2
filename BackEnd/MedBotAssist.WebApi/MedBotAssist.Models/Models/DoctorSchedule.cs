using System;
using System.Collections.Generic;

namespace MedBotAssist.Models.Models {
    public partial class DoctorSchedule
{
    public int ScheduleId { get; set; }

    public int? DoctorId { get; set; }

    public string? DayOfWeek { get; set; }

    public TimeOnly? StartTime { get; set; }

    public TimeOnly? EndTime { get; set; }

    public virtual Doctor? Doctor { get; set; }
}
}
