import sys
import io
import logging
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

logging.basicConfig(level=logging.INFO, format='%(levelname)s : %(message)s')

def fix_encoding(df):
    corrections = {
        "S\u00e3o Paulo": "São Paulo",
        "Bras\u00edlia": "Brasília",}
    df = df.replace(corrections)
    logging.info("Encoding fixed for city names")
    return df

def load_data():
    df = pd.read_csv('cleaned_restaurants.csv', encoding='utf-8-sig')
    df = fix_encoding(df)
    logging.info("Loaded: " +str(len(df)) + " restaurants")
    return df

def analyze_restaurant_count(df):
    logging.info("Analyzing restaurantns distribution by city...")
    city_counts = df['City'].value_counts()
    top_city = city_counts.idxmax()
    top_count = city_counts.max()
    top_pct = (top_count / len(df)) * 100

    return city_counts, top_city, top_count, top_pct

def analyze_average_rating(df):
    logging.info("Analyzing average rating by city...")
    avg_ratings = df.groupby('City')['Aggregate rating'].mean()
    avg_ratings_sorted = avg_ratings.sort_values(ascending=False)
    return avg_ratings, avg_ratings_sorted

def find_highest_rated_city(df, avg_ratings_sorted):
    logging.info("Finding highest rated city...")
    city_counts = df['City'].value_counts()
    filtered_ratings = avg_ratings_sorted[avg_ratings_sorted.index.isin(city_counts[city_counts>=5].index)]
    if len(filtered_ratings)==0:
        logging.warning("No cities with 5+ resturants found")
        best_city = avg_ratings_sorted.idmax()
        best_rating = avg_ratings_sorted.max()
        best_count = city_counts[best_city]
    
    else:
        best_city = filtered_ratings.idxmax()
        best_rating = filtered_ratings.max()
        best_count = city_counts[best_city]
    
    logging.info("Highest rated city: " + best_city)
    return best_city, best_count, best_rating

def problem_statement_1(city_counts, top_city, top_count, top_pct):
    print("\n" + "="*80)
    print("\nPROBLEM STATEMENT-1: CITY WITH HIGHEST NUMBER OF RESTAURANTS")
    print("="*80)

    print("\nTop 10 Cities by Number of Restaurants:")
    print("-" *70)
    print("Rank  | City               | Count  | % of Total")
    print("-" *70)

    for rank, (city, count) in enumerate(city_counts.head(10).items(),1):
        pct = ( count / city_counts.sum()) * 100
        print("{:4d} | {:<26s} | {:5d} | {:7.2f}%".format(rank, city[:26], count, pct))
    
    print("\n" + "-"*70)
    print("\nANSWER: ")
    print("-" *70)
    print("\nCity: " + top_city)
    print("\nRestaurant: " + str(top_count)) # type: ignore
    print("\nPercentage: " + "{:.2f}%".format(top_pct))
    print("-" *70)

def problem_statement_2(avg_ratings_sorted, df):
    print("\n" + "="*80)
    print("\nPROBLEM STATEMENT-2: AVERAGE RATING FOR RESTAURANTS IN EACH CITY")
    print("="*80)
    city_counts = df['City'].value_counts()

    print("\nTop 20 Cities by Average Rating:")
    print("-"*70)
    print("Rank  | City                     | Avg Rating | Count")
    print("-"*70)

    for rank, (city,rating) in enumerate(avg_ratings_sorted.head(20).items(),1):
        count = city_counts[city]
        print("{:4d} | {:<26s} | {:.4f}       | {:3d}".format(rank, city[:26], rating, count))
    print("-"*70)    
    print("ANSWER:")
    print("-"*70)
    print("Top 20 cities shown above")
    print("All" + str(len(avg_ratings_sorted)) + " cities exported to: problemstatement2_avg_rating_city.csv" )
    print("-"*70)
    sys.stdout.flush()

def problem_statement_3(best_city, best_rating, best_count):
    print("\n" + "="*80)
    print("\nPROBLEM STATEMENT-3: CITY WITH HIGHEST AVERAGE RATING (5+ restaurants)")
    print("="*80)

    print("\n" + "-"*70)
    print("\nANSWER:")
    print("-"*70)
    print("\nCity: " + best_city)
    print("\nAverage Rating: " + "{:.4f} / 5.0" .format(best_rating))
    print("\nNumber of Restaurants: " + str(best_count))
    print("-"*70)

def export_results(avg_ratings_sorted, df):
    logging.info("Exporting results...")
    city_counts = df['City'].value_counts()
    export_df = pd.DataFrame({'Rank' : range(1, len(avg_ratings_sorted) + 1),
                              'City' : avg_ratings_sorted.index,
                              'Average_Rating' : avg_ratings_sorted.values,
                              'Restaurant_Count' : [city_counts[city] for city in avg_ratings_sorted.index]})
    export_df.to_csv('problemstatement2_avg_rating_city.csv', index=False, encoding='utf-8-sig')
    logging.info("Exported: problemstatement2_avg_rating_city.csv")

COLORS = ['#4E79A7', '#F28E2B', '#59A14F', '#E15759','#76B7B2']
def create_visualizations(df, city_counts, avg_ratings_sorted, best_city, best_rating):
    logging.info("Creating visualizations...")
    top_10_cities = city_counts.head(10)
    top_10_ratings = [avg_ratings_sorted[city] for city in top_10_cities.index]
    fig, axes = plt.subplots(1, 3,figsize= (16,5))

    #Chart 1: Restaurant Count
    ax1 = axes[0]
    colors_chart = COLORS * (len(top_10_cities) // len(COLORS) + 1)
    bars1 = ax1.barh(range(len(top_10_cities)), top_10_cities.values, color=colors_chart[:len(top_10_cities)])
    ax1.set_yticks(range(len(top_10_cities)))
    ax1.set_yticklabels([c[:15] for c in top_10_cities.index])
    ax1.set_xlabel(' Number of Restaurants' , fontweight='bold')
    ax1.set_title('PS1: Top 10 Cities by Number of Restaurants', fontweight='bold', fontsize=11)
    ax1.invert_yaxis()
    ax1.grid(axis='x', alpha=0.3)

    for i, (bar, count) in enumerate(zip(bars1, top_10_cities.values)):
        ax1.text(count, i, ' ' + str(count), va='center', fontweight= 'bold',fontsize=9)

    #Chart 2: Average Rating
    ax2 = axes[1]
    colors_rating = plt.cm.RdYlGn(np.linspace(0.2, 0.8, len(top_10_cities)))
    bars2 = ax2.bar(range(len(top_10_cities)), top_10_ratings, color=colors_rating,
                    edgecolor='black', linewidth=1.5, alpha=0.8)
    ax2.set_xticks(range(len(top_10_cities)))
    ax2.set_xticklabels([c[:10] for c in top_10_cities.index], rotation=45, ha='right', fontsize=9)
    ax2.set_ylabel('Average Rating' , fontweight='bold')
    ax2.set_title('PS2: Average Rating by Top 10 Cities', fontweight='bold',fontsize=11)
    ax2.set_ylim([0,5])
    ax2.axhline(y=avg_ratings_sorted.mean(), color='red', linestyle='--',linewidth=2, label='Overall Avg')
    ax2.grid(axis='y', alpha=0.3)
    ax2.legend()

    for bar, rating in zip(bars2, top_10_ratings):
        height = bar.get_height()
        ax2.text(bar.get_x() + bar.get_width()/2., height, '{:.2f}'.format(rating), ha='center', va='bottom', fontweight='bold', fontsize=8)

    #Chart 3: Count vs Rating Scatter
    ax3 = axes[2]
    all_counts = [city_counts[city] for city in avg_ratings_sorted.index]
    all_ratings = avg_ratings_sorted.values
    scatter = ax3.scatter(all_counts, all_ratings, s=60, alpha=0.75, c=all_ratings, cmap='RdYlGn', edgecolors='black', linewidth=0.5)

    best_idx = np.where(avg_ratings_sorted.index == best_city)[0][0]
    ax3.scatter([all_counts[best_idx]], [all_ratings[best_idx]], s=300, color='red',
                marker='*', edgecolors='darkred', linewidth=2, label='Best City (Q3)', zorder=5)
    ax3.set_xlabel('Number of Restaurants', fontweight='bold')
    ax3.set_ylabel('Average Rating', fontweight='bold')
    ax3.set_title('PS3: Restaurant Count vs Average Rating', fontweight='bold', fontsize=11)
    ax3.grid(alpha=0.3)
    ax3.legend()
    
    cbar = plt.colorbar(scatter, ax=ax3)
    cbar.set_label('Rating', fontweight='bold')

    plt.tight_layout()
    plt.savefig('city_analysis_results.png', dpi=300, bbox_inches='tight')
    logging.info("Charts saved: city_analysis_results.png")
    plt.show()

def print_summary(top_city, top_count, best_city, best_rating, avg_ratings_sorted):
    print("\n" + "="*80)
    print("\nSUMMARY - ALL 3 PROBLEM STATEMENT ANSWERED")
    print("="*80)

    print("\nPS1: City with MOST restaurant")
    print("     " + top_city + " (" + str(top_count) + " restaurants)")
    
    print("\nPS2: Average rating for EACH city")
    print(" All " + str(len(avg_ratings_sorted)) + " cities shown in atble above")
    print("   Exported to: problemstatement2_avg_rating_city.csv")

    print("\nPS-3: City with HIGHEST average rating (5+ restaurants)")
    print("    " + best_city + " (" + "{:.4f}".format(best_rating) + "/5.0)")
    print("="*80 + "\n")

def main():
    print("\n" + "="*80)
    print("CITY ANALYSIS ")
    print("="*80 + "\n")

    try:
        global df
        df = load_data()

        city_counts, top_city, top_count, top_pct = analyze_restaurant_count(df)

        avg_ratings, avg_ratings_sorted = analyze_average_rating(df)

        best_city, best_rating, best_count = find_highest_rated_city(df, avg_ratings_sorted)

        problem_statement_1(city_counts, top_city, top_count, top_pct)
        problem_statement_2(avg_ratings_sorted,df)
        problem_statement_3(best_city, best_rating, best_count)

        export_results(avg_ratings_sorted, df)
        create_visualizations(df, city_counts, avg_ratings_sorted, best_city, best_rating)
        logging.info("Analysis Complete!")

    except Exception as e:
        logging.error("Error: " + str(e))
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()
 



