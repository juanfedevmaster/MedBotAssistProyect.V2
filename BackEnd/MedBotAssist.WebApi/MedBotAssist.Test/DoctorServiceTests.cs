using Xunit;
using System.Threading.Tasks;
using MedBotAssist.Models.Models;
using MedBotAssist.Persistance.Context;
using MedBotAssist.WebApi.Services.DoctorService;
using Microsoft.EntityFrameworkCore;
using System.Linq;

namespace MedBotAssist.Test
{
    public class DoctorServiceTests
    {
        private (DoctorService service, MedBotAssistDbContext context) CreateService(string dbName)
        {
            var options = new DbContextOptionsBuilder<MedBotAssistDbContext>()
                .UseInMemoryDatabase(databaseName: dbName)
                .Options;
            var context = new MedBotAssistDbContext(options);
            var service = new DoctorService(context);
            return (service, context);
        }

        [Fact]
        public async Task GetDoctorInfoAsync_ReturnsDoctorWithSpecialtyAndUser()
        {
            var (service, context) = CreateService(nameof(GetDoctorInfoAsync_ReturnsDoctorWithSpecialtyAndUser));
            var specialty = new Specialty { SpecialtyId = 1, SpecialtyName = "Cardiology" };
            var user = new User { UserId = 1, UserName = "docuser" };
            var doctor = new Doctor { DoctorId = 1, UserId = 1, SpecialtyId = 1, User = user, Specialty = specialty };

            context.Specialties.Add(specialty);
            context.Users.Add(user);
            context.Doctors.Add(doctor);
            context.SaveChanges();

            // Act
            var result = await service.GetDoctorInfoAsync(1);

            // Assert
            Assert.NotNull(result);
            Assert.NotNull(result.User);
            Assert.NotNull(result.Specialty);
            Assert.Equal("docuser", result.User.UserName);
            Assert.Equal("Cardiology", result.Specialty.SpecialtyName);
        }

        [Fact]
        public async Task GetDoctorInfoAsync_ReturnsNull_WhenNotFound()
        {
            var (service, _) = CreateService(nameof(GetDoctorInfoAsync_ReturnsNull_WhenNotFound));

            var result = await service.GetDoctorInfoAsync(999);

            Assert.Null(result);
        }

        [Fact]
        public async Task UpdateDoctorProfileAsync_UpdatesDoctor_WhenUserNameMatches()
        {
            var (service, context) = CreateService(nameof(UpdateDoctorProfileAsync_UpdatesDoctor_WhenUserNameMatches));
            var user = new User { UserId = 1, UserName = "docuser" };
            var doctor = new Doctor { DoctorId = 1, UserId = 1, User = user, MedicalLicenseNumber = "old", SpecialtyId = 1 };

            context.Users.Add(user);
            context.Doctors.Add(doctor);
            context.SaveChanges();

            var updatedDoctor = new Doctor { MedicalLicenseNumber = "new", SpecialtyId = 2 };

            var result = await service.UpdateDoctorProfileAsync(1, updatedDoctor, "docuser");

            Assert.NotNull(result);
            Assert.Equal("new", result.MedicalLicenseNumber);
            Assert.Equal(2, result.SpecialtyId);
        }

        [Fact]
        public async Task UpdateDoctorProfileAsync_ReturnsNull_WhenUserNameDoesNotMatch()
        {
            var (service, context) = CreateService(nameof(UpdateDoctorProfileAsync_ReturnsNull_WhenUserNameDoesNotMatch));
            var user = new User { UserId = 1, UserName = "docuser" };
            var doctor = new Doctor { DoctorId = 1, UserId = 1, User = user, MedicalLicenseNumber = "old", SpecialtyId = 1 };

            context.Users.Add(user);
            context.Doctors.Add(doctor);
            context.SaveChanges();

            var updatedDoctor = new Doctor { MedicalLicenseNumber = "new", SpecialtyId = 2 };

            var result = await service.UpdateDoctorProfileAsync(1, updatedDoctor, "otheruser");

            Assert.Null(result);
        }
    }
}
