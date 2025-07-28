using Xunit;
using Moq;
using System.Threading.Tasks;
using MedBotAssist.Interfaces;
using MedBotAssist.Models.DTOs;
using MedBotAssist.WebApi.Services.OrchestrationService;
using Microsoft.EntityFrameworkCore;
using System.Collections.Generic;
using System.Linq;
using System.Threading;
using MedBotAssist.Models.Models;
using MedBotAssist.Persistance.Context;

namespace MedBotAssist.Test
{
    public class AuthOrchestrationServiceTests
    {
        [Fact]
        public async Task LoginWithDoctorInfoAsync_ReturnsLoginResponseWithDoctorId()
        {
            // Arrange
            var options = new DbContextOptionsBuilder<MedBotAssistDbContext>()
                .UseInMemoryDatabase(databaseName: "TestDb_LoginWithDoctorInfo")
                .Options;

            using var context = new MedBotAssistDbContext(options);
            context.Users.Add(new User { UserId = 10, UserName = "doctor1" });
            context.Doctors.Add(new Doctor { DoctorId = 99, UserId = 10 });
            context.SaveChanges();

            var loginRequest = new LoginRequest { UserName = "doctor1", Password = "pass" };
            var loginResponse = new LoginResponse { UserName = "doctor1", Token = "token" };

            var mockAuthService = new Mock<IAuthService>();
            mockAuthService.Setup(s => s.LoginAsync(loginRequest)).ReturnsAsync(loginResponse);

            var service = new AuthOrchestrationService(mockAuthService.Object, context);

            // Act
            var result = await service.LoginWithDoctorInfoAsync(loginRequest);

            // Assert
            Assert.NotNull(result);
            Assert.Equal("doctor1", result.UserName);
            Assert.Equal("token", result.Token);
            Assert.Equal(99, result.DoctorId);
        }

        [Fact]
        public async Task LoginWithDoctorInfoAsync_ReturnsNull_WhenLoginFails()
        {
            // Arrange
            var loginRequest = new LoginRequest { UserName = "notfound", Password = "pass" };

            var mockAuthService = new Mock<IAuthService>();
            mockAuthService.Setup(s => s.LoginAsync(loginRequest)).ReturnsAsync((LoginResponse)null);

            var mockContext = new Mock<IMedBotAssistDbContext>();

            var service = new AuthOrchestrationService(mockAuthService.Object, mockContext.Object);

            // Act
            var result = await service.LoginWithDoctorInfoAsync(loginRequest);

            // Assert
            Assert.Null(result);
        }

        [Fact]
        public async Task RegisterAsync_CallsAuthServiceAndReturnsResult()
        {
            // Arrange
            var registerRequest = new RegisterRequest { UserName = "user", Password = "pass", Email = "mail@mail.com", FullName = "User" };
            var expected = "registered";

            var mockAuthService = new Mock<IAuthService>();
            mockAuthService.Setup(s => s.RegisterAsync(registerRequest)).ReturnsAsync(expected);

            var mockContext = new Mock<IMedBotAssistDbContext>();

            var service = new AuthOrchestrationService(mockAuthService.Object, mockContext.Object);

            // Act
            var result = await service.RegisterAsync(registerRequest);

            // Assert
            Assert.Equal(expected, result);
        }
    }
}