using MedBotAssist.Interfaces;
using MedBotAssist.Models.Models;
using MedBotAssist.Persistance.Context;
using MedBotAssist.WebApi.Services.AppointmentService;
using Microsoft.EntityFrameworkCore;
using Moq;


namespace MedBotAssist.Test
{
    public class AppointmentServiceTests
    {
        private readonly Mock<IMedBotAssistDbContext> _mockContext;
        private readonly Mock<DbSet<Appointment>> _mockSet;
        private readonly AppointmentService _service;
        private readonly List<Appointment> _appointments;

        public AppointmentServiceTests()
        {
            _appointments = new List<Appointment>
            {
                new Appointment { AppointmentId = 1, DoctorId = 1, PatientId = 1, AppointmentDate = new DateOnly(2024, 1, 1), Status = "Scheduled" },
                new Appointment { AppointmentId = 2, DoctorId = 2, PatientId = 2, AppointmentDate = new DateOnly(2024, 1, 2), Status = "Completed" }
            };

            var queryable = _appointments.AsQueryable();

            _mockSet = new Mock<DbSet<Appointment>>();
            _mockSet.As<IQueryable<Appointment>>().Setup(m => m.Provider).Returns(queryable.Provider);
            _mockSet.As<IQueryable<Appointment>>().Setup(m => m.Expression).Returns(queryable.Expression);
            _mockSet.As<IQueryable<Appointment>>().Setup(m => m.ElementType).Returns(queryable.ElementType);
            _mockSet.As<IQueryable<Appointment>>().Setup(m => m.GetEnumerator()).Returns(() => queryable.GetEnumerator());

            _mockContext = new Mock<IMedBotAssistDbContext>();
            _mockContext.Setup(c => c.Appointments).Returns(_mockSet.Object);

            _service = new AppointmentService(_mockContext.Object);
        }

        [Fact]
        public async Task GetAllAsync_ReturnsAllAppointments()
        {
            var options = new DbContextOptionsBuilder<MedBotAssistDbContext>()
                .UseInMemoryDatabase(databaseName: "TestDb") // This method is part of the Microsoft.EntityFrameworkCore namespace
                .Options;

            using var context = new MedBotAssistDbContext(options);
            context.Appointments.Add(new Appointment { AppointmentId = 1, DoctorId = 1 });
            context.Appointments.Add(new Appointment { AppointmentId = 2, DoctorId = 2 });
            context.SaveChanges();

            var service = new AppointmentService(context);

            var result = await service.GetAllAsync();

            Assert.Equal(2, result.Count());
        }

        [Fact]
        public async Task GetByIdAsync_ReturnsCorrectAppointment()
        {
            var options = new DbContextOptionsBuilder<MedBotAssistDbContext>()
                .UseInMemoryDatabase(databaseName: "TestDb_GetById")
                .Options;

            using var context = new MedBotAssistDbContext(options);
            context.Appointments.Add(new Appointment { AppointmentId = 1, DoctorId = 1 });
            context.Appointments.Add(new Appointment { AppointmentId = 2, DoctorId = 2 });
            context.SaveChanges();

            var service = new AppointmentService(context);

            var result = await service.GetByIdAsync(1);
            Assert.NotNull(result);
            Assert.Equal(1, result?.AppointmentId);
        }

        [Fact]
        public async Task CreateAsync_AddsAppointment()
        {
            var options = new DbContextOptionsBuilder<MedBotAssistDbContext>()
                .UseInMemoryDatabase(databaseName: "TestDb_CreateAsync")
                .Options;

            using var context = new MedBotAssistDbContext(options);
            var service = new AppointmentService(context);

            var newAppointment = new Appointment { AppointmentId = 3, DoctorId = 1, PatientId = 3, AppointmentDate = new DateOnly(2024, 2, 1), Status = "Scheduled" };

            var result = await service.CreateAsync(newAppointment);

            Assert.NotNull(await context.Appointments.FindAsync(3));
            Assert.Equal(newAppointment, result);
        }

        [Fact]
        public async Task DeleteAsync_RemovesAppointment()
        {
            _mockSet.Setup(m => m.FindAsync(It.IsAny<object[]>()))
                .ReturnsAsync((object[] ids) => _appointments.FirstOrDefault(a => a.AppointmentId == (int)ids[0]));
            _mockSet.Setup(m => m.Remove(It.IsAny<Appointment>())).Callback<Appointment>(a => _appointments.Remove(a));
            _mockContext.Setup(m => m.SaveChangesAsync(It.IsAny<CancellationToken>())).ReturnsAsync(1);

            var result = await _service.DeleteAsync(1);

            Assert.True(result);
            Assert.DoesNotContain(_appointments, a => a.AppointmentId == 1);
        }

        [Fact]
        public async Task UpdateAsync_UpdatesAppointment()
        {
            var options = new DbContextOptionsBuilder<MedBotAssistDbContext>()
                .UseInMemoryDatabase(databaseName: "TestDb_UpdateAsync")
                .Options;

            using var context = new MedBotAssistDbContext(options);
            // Agrega la cita original
            context.Appointments.Add(new Appointment { AppointmentId = 1, DoctorId = 1, PatientId = 1, AppointmentDate = new DateOnly(2024, 1, 1), Status = "Scheduled" });
            context.SaveChanges();

            var service = new AppointmentService(context);

            // Crea el objeto actualizado
            var updated = new Appointment { AppointmentId = 1, DoctorId = 1, PatientId = 1, AppointmentDate = new DateOnly(2024, 1, 10), Status = "Rescheduled" };

            var result = await service.UpdateAsync(updated);

            Assert.NotNull(result);
            Assert.Equal("Rescheduled", result?.Status);
            Assert.Equal(new DateOnly(2024, 1, 10), result?.AppointmentDate);
        }
    }
}
