# 📊 Analytics AI Tool

A powerful Streamlit application that converts natural language queries into SQL and provides instant data visualization and analysis.

## 🚀 Features

- **Natural Language to SQL**: Convert plain English questions into SQL queries using OpenAI
- **Multiple Database Support**: Works with SQLite, MySQL, and PostgreSQL
- **Auto Visualizations**: Automatically generates charts and graphs from query results
- **Query History**: Keep track of all your queries and results
- **Schema Explorer**: Browse database tables and their structures
- **Sample Data**: Built-in sample data for testing and demonstration
- **Export Results**: Download query results as CSV files
- **SQL Explanation**: Get plain English explanations of generated SQL queries

## 🛠️ Installation

1. **Clone or download this project**

2. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

3. **Set up environment variables**:
   - Copy `.env.example` to `.env`
   - Add your OpenAI API key:
     ```
     OPENAI_API_KEY=your_openai_api_key_here
     ```

4. **Run the application**:
   ```bash
   streamlit run app.py
   ```

## 🔧 Configuration

### Environment Variables

- `OPENAI_API_KEY`: Your OpenAI API key (required)
- `DATABASE_URL`: Database connection string (default: SQLite)
- `DATABASE_TYPE`: Database type (sqlite/mysql/postgresql)

### Database Setup

#### SQLite (Default)
No additional setup required. The app will create a local SQLite database.

#### MySQL
```bash
DATABASE_URL=mysql+pymysql://username:password@host:port/database
DATABASE_TYPE=mysql
```

#### PostgreSQL
```bash
DATABASE_URL=postgresql://username:password@host:port/database
DATABASE_TYPE=postgresql
```

## 📖 Usage

1. **Start the application** and navigate to the web interface
2. **Connect to database** using the sidebar button
3. **Create sample data** (optional) for testing
4. **Enter your question** in natural language, such as:
   - "Show me total sales by product"
   - "What are the top 10 customers by age?"
   - "Show sales trends over the last month"
5. **Click "Generate & Execute Query"** to see results
6. **View automatic visualizations** and download results if needed

## 💡 Example Queries

- "Show me the top 5 products by sales amount"
- "What is the average age of customers in each city?"
- "Show sales trends over time"
- "Which region has the highest total sales?"
- "List all customers older than 30"
- "Show monthly sales summary"

## 🏗️ Architecture

```
├── app.py              # Main Streamlit application
├── config.py           # Configuration settings
├── database.py         # Database connection and operations
├── sql_generator.py    # OpenAI integration for SQL generation
├── requirements.txt    # Python dependencies
├── .env.example       # Environment variables template
└── README.md          # This file
```

## 🔒 Security Features

- **SQL Injection Prevention**: Validates queries to prevent destructive operations
- **Read-only Operations**: Blocks INSERT, UPDATE, DELETE, DROP operations
- **API Key Protection**: Secure handling of OpenAI API credentials
- **Query Validation**: Automatic validation of generated SQL queries

## 🎨 Customization

### Adding New Database Types
Extend the `DatabaseManager` class in `database.py` to support additional database types.

### Custom Visualizations
Modify the `generate_visualizations()` function in `app.py` to add custom chart types.

### SQL Generation Prompts
Customize the SQL generation prompts in `sql_generator.py` for domain-specific requirements.

## 🐛 Troubleshooting

### Common Issues

1. **OpenAI API Key Error**
   - Ensure your API key is correctly set in the `.env` file
   - Check that your OpenAI account has sufficient credits

2. **Database Connection Issues**
   - Verify database credentials and connection string
   - Ensure the database server is running and accessible

3. **Query Generation Problems**
   - Check that your database schema is properly loaded
   - Try simpler, more specific natural language queries

### Error Messages

- `Database connection failed`: Check your database configuration
- `SQL generation failed`: Verify OpenAI API key and connectivity
- `Query execution failed`: Review the generated SQL for syntax errors

## 📊 Sample Data Schema

The application includes sample tables:

### Sales Table
- `id`: Unique identifier
- `product`: Product name
- `sales_amount`: Sales amount in dollars
- `sales_date`: Date of sale
- `region`: Sales region

### Customers Table
- `customer_id`: Unique customer identifier
- `customer_name`: Customer name
- `age`: Customer age
- `city`: Customer city

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

## 📄 License

This project is open source and available under the MIT License.

## 🆘 Support

For issues and questions:
1. Check the troubleshooting section
2. Review the example queries
3. Ensure all dependencies are properly installed
4. Verify your OpenAI API key is valid

## 🔮 Future Enhancements

- Support for more database types
- Advanced visualization options
- Query optimization suggestions
- Natural language result explanations
- Collaborative query sharing
- Advanced analytics and insights
