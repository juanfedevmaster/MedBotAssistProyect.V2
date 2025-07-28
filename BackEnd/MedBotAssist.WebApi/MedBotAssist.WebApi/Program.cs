using MedBotAssist.Interfaces;
using MedBotAssist.Persistance.Context;
using MedBotAssist.WebApi.Services.AuthService;
using Microsoft.EntityFrameworkCore;
using Microsoft.AspNetCore.Authentication.JwtBearer;
using Microsoft.IdentityModel.Tokens;
using System.Text;
using Microsoft.OpenApi.Models;
using MedBotAssist.WebApi.Services.ClinicalSummaryService;
using MedBotAssist.WebApi.Services.PatientService;
using MedBotAssist.WebApi.Services.AppointmentService;
using MedBotAssist.WebApi.Services.DoctorService;
using MedBotAssist.WebApi.Services.OrchestrationService;
using MedBotAssist.WebApi.Services.MedicalNoteService;

namespace MedBotAssist.WebApi
{
    public class Program
    {
        public static void Main(string[] args)
        {
            var builder = WebApplication.CreateBuilder(args);

            // Add services to the container.
            builder.Services.AddControllers();

            // Register the MedBotAssist DataBase
            builder.Services.AddDbContext<MedBotAssistDbContext>(options =>
                options.UseSqlServer(builder.Configuration.GetConnectionString("MedBotAssistConnection")));

            // Register the AuthService
            builder.Services.AddScoped<IMedBotAssistDbContext, MedBotAssistDbContext>();
            builder.Services.AddScoped<IAuthService, AuthService>();
            builder.Services.AddScoped<IClinicalSummaryService, ClinicalSummaryService>();
            builder.Services.AddScoped<IPatientService, PatientService>();
            builder.Services.AddScoped<IAppointmentService, AppointmentService>();
            builder.Services.AddScoped<IDoctorService, DoctorService>();
            builder.Services.AddScoped<IAuthOrchestrationService, AuthOrchestrationService>();
            builder.Services.AddScoped<IMedicalNoteService, MedicalNoteService>();

            // JWT Authentication configuration
            var jwtKey = builder.Configuration["JwtSettings:Secret"]; // Use a secure key in production
            var jwtIssuer = builder.Configuration["JwtSettings:Issuer"];

            builder.Services.AddAuthentication(options =>
            {
                options.DefaultAuthenticateScheme = JwtBearerDefaults.AuthenticationScheme;
                options.DefaultChallengeScheme = JwtBearerDefaults.AuthenticationScheme;
            })
            .AddJwtBearer(options =>
            {
                options.TokenValidationParameters = new TokenValidationParameters
                {
                    ValidateIssuer = true,
                    ValidateAudience = false,
                    ValidateLifetime = true,
                    ValidateIssuerSigningKey = true,
                    ValidIssuer = jwtIssuer,
                    IssuerSigningKey = new SymmetricSecurityKey(Encoding.UTF8.GetBytes(jwtKey))
                };
            });

            // Swagger/OpenAPI
            builder.Services.AddEndpointsApiExplorer();
            builder.Services.AddSwaggerGen(options =>
            {
                options.AddSecurityDefinition("Bearer", new OpenApiSecurityScheme
                {
                    Name = "Authorization",
                    Type = SecuritySchemeType.Http,
                    Scheme = "Bearer",
                    BearerFormat = "JWT",
                    In = ParameterLocation.Header,
                    Description = "Enter 'Bearer' [space] and then your valid token in the text input below.\nExample: \"Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6...\""
                });

                options.AddSecurityRequirement(new OpenApiSecurityRequirement
                {
                    {
                        new OpenApiSecurityScheme
                        {
                            Reference = new OpenApiReference
                            {
                                Type = ReferenceType.SecurityScheme,
                                Id = "Bearer"
                            }
                        },
                        Array.Empty<string>()
                    }
                });
            });

            builder.Services.AddCors(options =>
            {
                options.AddPolicy("AllowFrontend", policy =>
                {
                    policy.WithOrigins("http://localhost:3000")
                          .AllowAnyHeader()
                          .AllowAnyMethod()
                          .AllowCredentials();
                });
                options.AddPolicy("AllowBackEndAI", policy =>
                {
                    policy.WithOrigins("http://localhost:8000")
                          .AllowAnyHeader()
                          .AllowAnyMethod()
                          .AllowCredentials();
                });
                options.AddPolicy("AllowFrontEndProduction", policy =>
                {
                    policy.WithOrigins("https://medbotassistui-bueue9cwczabe5cm.eastus2-01.azurewebsites.net")
                          .AllowAnyHeader()
                          .AllowAnyMethod()
                          .AllowCredentials();
                });
                options.AddPolicy("AllowBackEndAIProduction", policy =>
                {
                    policy.WithOrigins("https://medbotassistai-a2b5ffdrajbehtb0.eastus2-01.azurewebsites.net")
                          .AllowAnyHeader()
                          .AllowAnyMethod()
                          .AllowCredentials();
                });
            });

            var app = builder.Build();

            if (app.Environment.IsDevelopment())
            {
                app.UseCors("AllowFrontend");
                app.UseCors("AllowBackEndAI");
            }
            else
            {
                app.UseCors("AllowFrontEndProduction");
                app.UseCors("AllowBackEndAIProduction");
            }

            app.UseSwagger();
            app.UseSwaggerUI();

            // Require JWT token for all controllers
            app.UseAuthentication();
            app.UseAuthorization();

            app.MapControllers();

            app.Run();
        }
    }
}