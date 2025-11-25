import streamlit as st
from utlis import key_glossary
from streamlit_extras.stylable_container import stylable_container
st.set_page_config(
            page_title="RGM Dashboard",
            layout="wide",
            page_icon = 'sigmoid_logo.png',
            initial_sidebar_state="collapsed")
def render_navbar_promo():
        # Adding Bootstrap CSS
    st.markdown('<link rel="stylesheet" href="https://maxcdn.bootstrapcdn.com/bootstrap/4.0.0/css/bootstrap.min.css" integrity="sha384-Gn5384xqQ1aoWXA+058RXPxPg6fy4IWvTNh0E263XmFcJlSAwiGgFAW/dAiS6JXm" crossorigin="anonymous">', unsafe_allow_html=True)

    # Adding custom CSS for navbar
    st.markdown("""
        <style>
            .navbar {
                background: linear-gradient(90deg, #D91E18, orange);
                font-family: Arial, sans-serif; /* Custom font style */
            }
            .navbar-brand {
                color: white !important; /* Setting text color to white */
                font-size: 24px; /* Custom font size */
                # font-weight: bold; /* Custom font weight */
                text-decoration: none; /* Remove underline */
            }
            .navbar-button {
                background-color: white !important;
                color: red !important;
                border: 1px solid red;
            }
            .navbar-button:hover {
                background-color: red !important;
                color: white !important;
            }
        </style>
        """, unsafe_allow_html=True)

    # Navbar content
    st.markdown("""
        <nav class="navbar fixed-top navbar-expand-lg navbar-dark" style="margin-top: 18px; margin-bottom: 0px;">
        <div class="container-fluid">
            <img src="https://i.im.ge/2024/05/30/KLEPIh.Screenshot-2024-05-30-at-10-20-29AM.png" alt="Logo1" style="height: 55px; margin-right: -10px; margin-top: 20px; margin-bottom: -10px">
            <img src="https://i.im.ge/2024/03/21/RKWdrM.Sigmoid-Logo.png" alt="Logo2" style="height: 60px; margin-left: 1400px; margin-top: 20px; margin-bottom: -10px">
            <div class="navbar-collapse justify-content-end">
            </div>
        </div>
    </nav>
        """, unsafe_allow_html=True)

render_navbar_promo()

# col1, col2, col3=st.columns([3,6,3])
# with col2:
#     st.markdown(
#         """
#         <style>
#             .bordered {
#                 border: 5px solid #e67e22; /* Orange color */
#                 padding: 10px;
#                 border-radius: 5px;
#             }
#         </style>
#         """,
#         unsafe_allow_html=True,
#     )

#     # Glossary header
#     st.markdown('<p style="font-family: Arial; font-size: 18px; text-align: center;"><strong>Glossary</strong></p>', unsafe_allow_html=True)

#     # Glossary items
#     st.markdown("""
#         <p class="bordered" style="font-family: Arial; font-size: 18px;">
#         <strong>Fair Share:</strong> It pertains to equitable distribution of  revenue across all retailers or manufacturers within a category, without using specific filters.<br><br>
#         <strong>Price Elasticity:</strong> Price elasticity measures the responsiveness of consumers to changes in price. E.g., A price elasticity <-2.0,for example, is considered more price elastic and 5% price increase will result in roughly 10% volume loss.<br><br>  
#         <strong>Cross Price Elasticity:</strong> Cross price elasticity refers to how the demand for one product changes in response to a change in the price of another related product. It quantifies the percentage change in the quantity demanded of one product when the price of another product changes by one percent.    E.g A Cross Price Elasticty < 1 , for example, is considered less elastic and 5% price increase in competitor price will result in 5% gain in own volume.<br><br>
#         <strong>Distribution Elasticity:</strong> Distribution elasticity provide insights on impact of products distribution on the volume. For every 1%-point increase in product’s ACV weighted distribution (Wtd. %ACV ) or Total Distribution Points (TDP) , distribution elasticity of 0.6 results in 0.6% increase in product’s volume.<br><br>
#         <strong>Current Price:</strong> It shows last year average price.<br><br>
#         <strong>Current Distribution:</strong> It shows last year average distribution.<br><br>
#         <strong>Current Competitor Price:</strong> It shows last year average competitor price.
#         </p>
#         """, 
#         unsafe_allow_html=True
#     )
t1,t2= st.columns([0.9,0.05])
with t2:
     with stylable_container(
                                    key="green_button1",
                                    css_styles="""
                                        button {
                                            background-color: #ffffff;
                                            color: #205B97;
                                            border-radius: 10px;
                                        }
                                        """,
                                ):
        if st.button('Return', key=10, use_container_width=True):
                st.switch_page("./pages/Optimal Promotion.py")
with t1:
        st.markdown(
                   """
                    <div style="display: flex; justify-content: left; text-align: left;">
                        <p style="font-size: 30px; color: #205B97; font-weight: bold; font-family: 'Graphik';">
                            GLOSSARY
                        </p>
                    </div>
                    """,
                unsafe_allow_html=True
                )

key_glossary(
                    "It pertains to equitable distribution of  revenue across all retailers or manufacturers within a category, without using specific filters.",
                    'Fair Share',
                    'https://i.im.ge/2024/05/15/KQF8NW.Price-Elasticity.png'
                   )
st.write(" ")
key_glossary(
                    "Price elasticity measures the responsiveness of consumers to changes in price. E.g., A price elasticity = -2.0,for example, is considered more price elastic and 5% price increase will result in roughly 10% volume loss.",
                    'Price Elasticity',
                    'https://i.im.ge/2024/05/15/KQF8NW.Price-Elasticity.png'
                   )
st.write(" ")
key_glossary(
                    "Cross price elasticity refers to how the demand for one product changes in response to a change in the price of another related product. It quantifies the percentage change in the quantity demanded of one product when the price of another product changes by one percent.    E.g A Cross Price Elasticty = 1 , for example, is considered less elastic and 5% price increase in competitor price will result in 5% gain in own volume.",
                    'Cross Price Elasticity',
                    'https://i.im.ge/2024/05/15/KQFPV4.Cross-Price-Elasticity.png'
                   )
st.write(" ")
key_glossary(
                    "Distribution elasticity provide insights on impact of products distribution on the volume. For every 1%-point increase in product’s ACV weighted distribution (Wtd. %ACV ) or Total Distribution Points (TDP) , distribution elasticity of 0.6 results in 0.6% increase in product’s volume.",
                    'Distribution Elasticity',
                    'https://i.im.ge/2024/05/15/KQFxMP.Distribution-Elasticity.png'
                   )
st.write(" ")

key_glossary(
                    "It shows last year average price.",
                    'Current Price',
                    'https://i.im.ge/2024/05/15/KQFCgp.Current-Price.png'
                   )
st.write(" ")
key_glossary(
                    "It shows last year average distribution.",
                    'Current Distribution',
                    'https://i.im.ge/2024/05/15/KQFA5q.Current-Distribution.png'
                   )
st.write(" ")
key_glossary(
                    "It shows last year average competitor price",
                    'Current Competitor Price',
                    'https://i.im.ge/2024/05/15/KQFyrC.Current-Competitor-Price.png'
                   )
st.write(" ")
key_glossary(
                    "A temporary discount on the regular price of a product to stimulate sales and attract customers. TPRs are often used to boost short-term revenue or clear out inventory.",
                    'TPR (Temporary Price Reduction)',
                    'https://i.im.ge/2024/05/30/KLEVdW.TPR.png'
                   )
st.write(" ")
key_glossary(
                    "A type of promotion where a product is highlighted in marketing materials, such as flyers, catalogs, or online banners. Features increase product visibility and awareness, driving consumer interest and sales.",
                    'Feature',
                    'https://i.im.ge/2024/05/30/KLEc8P.Feature.png'
                   )
st.write(" ")
key_glossary(
                    "A promotional strategy where products are prominently showcased in physical. Special displays, end caps, or eye-catching arrangements draw attention to the promoted items, encouraging impulse purchases and increasing sales.",
                    'Display',
                    'https://i.im.ge/2024/05/30/KLEYuq.Display.png'
                   )
st.write(" ")
key_glossary(
                    "The percentage of customers who take advantage of a promotional offer out of the total number of customers who were exposed to the offer. It measures the effectiveness of the promotion in converting potential customers into actual buyers.",
                    'Redemption Rate',
                    'https://i.im.ge/2024/05/30/KLE8Q1.Redemption-Rate.png'
                   )
st.write(" ")
key_glossary(
                    "A performance measure used to evaluate the efficiency or profitability of an investment. In promotions, ROI calculates the gain or loss generated relative to the amount invested in the promotional activity. It helps to determine the financial return of marketing efforts.",
                    'ROI (Return on Investment)',
                    'https://i.im.ge/2024/05/30/KLEWxm.ROI.png'
                   )
st.write(" ")
key_glossary(
                    "The increase in sales or customer engagement attributed to a specific promotion or marketing activity. Uplift measures the positive impact of the promotion by comparing sales or engagement levels before and during the promotion period. It helps assess the effectiveness of the promotional strategy in driving additional business.",
                    'Uplift',
                    'https://i.im.ge/2024/05/30/KLEZnr.Uplift.png'
                   )
