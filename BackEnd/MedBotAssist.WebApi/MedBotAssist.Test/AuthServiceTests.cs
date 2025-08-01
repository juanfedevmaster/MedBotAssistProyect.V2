using Xunit;
using Moq;
using System.Threading.Tasks;
using MedBotAssist.Interfaces;
using MedBotAssist.Models.DTOs;
using MedBotAssist.Models.Models;
using Microsoft.Extensions.Configuration;
using Microsoft.EntityFrameworkCore;
using System.Collections.Generic;
using System.Linq;
using System.Threading;
using MedBotAssist.Persistance.Context;

namespace MedBotAssist.Test
{
    public class AuthServiceTests
    {
        [Fact]
        public async Task LoginAsync_ReturnsLoginResponse_WhenCredentialsAreValid()
        {
            // Arrange
            var options = new DbContextOptionsBuilder<MedBotAssistDbContext>()
                .UseInMemoryDatabase(databaseName: "TestDb_LoginAsync_Valid")
                .Options;

            using var context = new MedBotAssistDbContext(options);
            context.Users.Add(new User { UserId = 1, UserName = "user", Password = BCrypt.Net.BCrypt.HashPassword("pass"), Role = "Admin" });
            context.SaveChanges();

            var mockConfig = new Mock<IConfiguration>();
            // Use a base64-encoded version of your secret
            var secret = Convert.ToBase64String(System.Text.Encoding.UTF8.GetBytes("mysupersecretkeymysupersecretkey"));
            mockConfig.Setup(c => c["JwtSettings:Secret"]).Returns(secret);

            var mockSection = new Mock<IConfigurationSection>();
            mockSection.Setup(s => s.Value).Returns(secret);
            mockConfig.Setup(c => c.GetSection("JwtSettings:Secret")).Returns(mockSection.Object);
            mockConfig.Setup(c => c.GetSection("JwtSettings")["Secret"]).Returns(secret);
            mockConfig.Setup(c => c["JwtSettings:Issuer"]).Returns("TestIssuer");
            mockConfig.Setup(c => c["JwtSettings:Audience"]).Returns("TestAudience");
            mockConfig.Setup(c => c["JwtSettings:ExpirationMinutes"]).Returns("60"); // <-- valor numérico válido

            // Mock de StorageAccount
            mockConfig.Setup(c => c["StorageAccount:accountName"]).Returns("testaccount");
            mockConfig.Setup(c => c["StorageAccount:accountKey"]).Returns("dGVzdGtleQ=="); // "testkey" en base64
            mockConfig.Setup(c => c["StorageAccount:containerName"]).Returns("testcontainer");

            var service = new MedBotAssist.WebApi.Services.AuthService.AuthService(context, mockConfig.Object);

            var request = new LoginRequest { UserName = "user", Password = "pass" };

            // Act
            var result = await service.LoginAsync(request);

            // Assert
            Assert.NotNull(result);
            Assert.Equal("user", result.UserName);
            Assert.False(string.IsNullOrEmpty(result.Token));
        }

        [Fact]
        public async Task LoginAsync_ReturnsNull_WhenUserNotFound()
        {
            // Arrange
            var options = new DbContextOptionsBuilder<MedBotAssistDbContext>()
                .UseInMemoryDatabase(databaseName: "TestDb_LoginAsync_NotFound")
                .Options;

            using var context = new MedBotAssistDbContext(options);

            var mockConfig = new Mock<IConfiguration>();

            var service = new MedBotAssist.WebApi.Services.AuthService.AuthService(context, mockConfig.Object);

            var request = new LoginRequest { UserName = "nouser", Password = "pass" };

            // Act
            var result = await service.LoginAsync(request);

            // Assert
            Assert.Null(result);
        }

        [Fact]
        public async Task RegisterAsync_ReturnsSuccessMessage()
        {
            // Arrange
            var options = new DbContextOptionsBuilder<MedBotAssistDbContext>()
                .UseInMemoryDatabase(databaseName: "TestDb_RegisterAsync")
                .Options;

            using var context = new MedBotAssistDbContext(options);
            context.Roles.Add(new Role { RoleId = 1, RoleName = "User" });
            context.SaveChanges();

            var role = await context.Roles.FirstOrDefaultAsync(r => r.RoleName.Equals("User"));
            if (role == null)
                throw new InvalidOperationException("Role 'User' not found.");
            

            var mockConfig = new Mock<IConfiguration>();

            var service = new MedBotAssist.WebApi.Services.AuthService.AuthService(context, mockConfig.Object);

            var request = new RegisterRequest { UserName = "newuser", Password = "pass", Email = "mail@mail.com", FullName = "User" };

            // Act
            var result = await service.RegisterAsync(request);

            // Assert
            Assert.Equal("User successfully registered and role assigned.", result);
            Assert.Single(context.Users.Where(u => u.UserName.Equals("newuser")));
            Assert.Single(context.UserRoles.Where(ur => ur.RoleId == 1));
        }
    }
}
